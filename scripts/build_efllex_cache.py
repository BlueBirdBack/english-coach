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
LEVEL_RANK = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5}
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


def best_entry_key(entry: tuple[str, str, str, str, float, float, str]) -> tuple[int, float, str, str]:
    """Sort key for choosing one deterministic best row for a word.

    Lower CEFR rank wins first because the cache represents the earliest
    learner level with evidence. Higher total frequency then wins among rows at
    the same level. Tag and word are final stable tie-breakers.
    """

    word, _normalized, tag, cefr, _score, total_freq, _source = entry
    return (LEVEL_RANK.get(cefr, 99), -total_freq, tag, word)


def iter_rows(tsv_path: Path):
    with tsv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            yield row


def _group_entries_by_word(
    rows: list[tuple[str, str, str, str, float, float, str]],
) -> dict[str, list[tuple[str, str, str, str, float, float, str]]]:
    grouped: dict[str, list[tuple[str, str, str, str, float, float, str]]] = {}
    for row in rows:
        grouped.setdefault(row[1], []).append(row)
    return grouped


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
                id INTEGER PRIMARY KEY,
                word TEXT NOT NULL,
                normalized_word TEXT NOT NULL,
                tag TEXT NOT NULL,
                cefr TEXT NOT NULL,
                level_score REAL NOT NULL,
                total_freq REAL NOT NULL,
                source TEXT NOT NULL
            );

            CREATE INDEX idx_entries_word ON entries(normalized_word);
            CREATE INDEX idx_entries_cefr ON entries(cefr);
            CREATE INDEX idx_entries_word_tag ON entries(normalized_word, tag);

            CREATE TABLE word_best (
                normalized_word TEXT PRIMARY KEY,
                word TEXT NOT NULL,
                cefr TEXT NOT NULL,
                tag TEXT NOT NULL,
                level_score REAL NOT NULL,
                total_freq REAL NOT NULL,
                source TEXT NOT NULL
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
            INSERT INTO entries
            (word, normalized_word, tag, cefr, level_score, total_freq, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        best_rows = [
            sorted(entries, key=best_entry_key)[0]
            for entries in _group_entries_by_word(rows).values()
        ]
        conn.executemany(
            """
            INSERT INTO word_best
            (word, normalized_word, tag, cefr, level_score, total_freq, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            best_rows,
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
