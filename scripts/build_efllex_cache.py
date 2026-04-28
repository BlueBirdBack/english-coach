#!/usr/bin/env python3
"""Build a compact SQLite cache from the static EFLLex TSV.

Usage:
    python scripts/build_efllex_cache.py \
        references/EFLLex_NLP4J \
        references/efllex.sqlite

The runtime English Coach should query the SQLite file instead of scanning the
large TSV at request time.
"""

from __future__ import annotations

import argparse
import csv
import re
import sqlite3
from pathlib import Path

LEVELS = ("a1", "a2", "b1", "b2", "c1")
WORD_RE = re.compile(r"^[\w'’.-]+$", re.UNICODE)


def normalize_word(value: str) -> str:
    return value.strip().replace("’", "'").lower()


def parse_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def choose_cefr(row: dict[str, str]) -> tuple[str | None, float]:
    """Choose the easiest CEFR level where the word has non-zero frequency.

    EFLLex gives per-level frequency columns. For learner lookup, the earliest
    level with evidence is usually the most useful teaching level. The score is
    that level's frequency, saved for debugging/tie-breaking.
    """

    for level in LEVELS:
        score = parse_float(row.get(f"level_freq@{level}", "0"))
        if score > 0:
            return level.upper(), score
    return None, 0.0


def iter_rows(tsv_path: Path):
    with tsv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            yield row


def build_cache(tsv_path: Path, db_path: Path) -> tuple[int, int]:
    if not tsv_path.exists():
        raise FileNotFoundError(tsv_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA synchronous=OFF")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.executescript(
            """
            CREATE TABLE entries (
                word TEXT NOT NULL,
                normalized_word TEXT NOT NULL,
                tag TEXT NOT NULL,
                cefr TEXT NOT NULL,
                level_score REAL NOT NULL,
                total_freq REAL NOT NULL,
                source TEXT NOT NULL,
                PRIMARY KEY (normalized_word, tag)
            );

            CREATE INDEX idx_entries_word ON entries(normalized_word);
            CREATE INDEX idx_entries_cefr ON entries(cefr);

            CREATE VIEW word_best AS
            SELECT
                normalized_word,
                word,
                cefr,
                tag,
                level_score,
                total_freq,
                source
            FROM entries e
            WHERE NOT EXISTS (
                SELECT 1 FROM entries better
                WHERE better.normalized_word = e.normalized_word
                  AND (
                    CASE better.cefr
                      WHEN 'A1' THEN 1 WHEN 'A2' THEN 2 WHEN 'B1' THEN 3
                      WHEN 'B2' THEN 4 WHEN 'C1' THEN 5 ELSE 99 END
                  ) < (
                    CASE e.cefr
                      WHEN 'A1' THEN 1 WHEN 'A2' THEN 2 WHEN 'B1' THEN 3
                      WHEN 'B2' THEN 4 WHEN 'C1' THEN 5 ELSE 99 END
                  )
            );

            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )

        inserted = 0
        skipped = 0
        source_name = tsv_path.name
        rows = []
        for row in iter_rows(tsv_path):
            word = (row.get("word") or "").strip()
            tag = (row.get("tag") or "").strip()
            normalized = normalize_word(word)
            cefr, score = choose_cefr(row)
            total_freq = parse_float(row.get("total_freq@total", "0"))

            if not word or not normalized or not tag or not cefr:
                skipped += 1
                continue
            if not WORD_RE.match(normalized):
                # Keep the DB focused on lookup-friendly lexical entries.
                skipped += 1
                continue

            rows.append((word, normalized, tag, cefr, score, total_freq, source_name))
            inserted += 1

        conn.executemany(
            """
            INSERT OR REPLACE INTO entries
            (word, normalized_word, tag, cefr, level_score, total_freq, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.executemany(
            "INSERT INTO metadata(key, value) VALUES (?, ?)",
            [
                ("source", str(tsv_path)),
                ("source_name", source_name),
                ("schema_version", "1"),
                ("cefr_policy", "earliest_nonzero_level_frequency"),
                ("inserted_rows", str(inserted)),
                ("skipped_rows", str(skipped)),
            ],
        )
        conn.commit()
        conn.execute("VACUUM")
        return inserted, skipped
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tsv", type=Path, help="Path to EFLLex TSV file")
    parser.add_argument("sqlite", type=Path, help="Output SQLite cache path")
    args = parser.parse_args()

    inserted, skipped = build_cache(args.tsv, args.sqlite)
    size = args.sqlite.stat().st_size
    print(f"Built {args.sqlite}")
    print(f"Inserted rows: {inserted}")
    print(f"Skipped rows: {skipped}")
    print(f"SQLite size: {size} bytes")


if __name__ == "__main__":
    main()
