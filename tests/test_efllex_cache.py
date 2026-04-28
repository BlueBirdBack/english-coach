from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_efllex_cache import build_cache, choose_cefr, normalize_word  # noqa: E402
from scripts.efllex_lookup import CefrLookup  # noqa: E402


@pytest.fixture(autouse=True)
def reset_cefr_lookup_singleton():
    instance = CefrLookup._instance
    if instance is not None:
        instance.conn.close()
    CefrLookup._instance = None
    yield
    instance = CefrLookup._instance
    if instance is not None:
        instance.conn.close()
    CefrLookup._instance = None


def write_sample_tsv(path: Path) -> None:
    path.write_text(
        "\t".join(
            [
                "word",
                "tag",
                "level_freq@a1",
                "level_freq@a2",
                "level_freq@b1",
                "level_freq@b2",
                "level_freq@c1",
                "total_freq@total",
            ]
        )
        + "\n"
        + "\n".join(
            [
                "Plausible\tJJ\t0\t0\t0\t0.3154\t0\t0.045",
                "work\tVB\t1649.5279\t10\t5\t0\t0\t1250.2909",
                "Work\tNN\t0\t9\t0\t0\t0\t3000",
                "rock’n’roll\tNN\t0\t0\t1.5\t0\t0\t1.5",
                "missingtag\t\t1\t0\t0\t0\t0\t1",
                "unknown\tJJ\t0\t0\t0\t0\t0\t0",
                "two words\tNN\t1\t0\t0\t0\t0\t1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_normalize_word_strips_lowercases_and_normalizes_curly_apostrophes():
    assert normalize_word("  Rock’n’Roll  ") == "rock'n'roll"
    assert CefrLookup.normalize("  Rock’n’Roll  ") == "rock'n'roll"


def test_choose_cefr_returns_earliest_nonzero_level():
    row = {
        "level_freq@a1": "0",
        "level_freq@a2": "0",
        "level_freq@b1": "2.5",
        "level_freq@b2": "9.9",
        "level_freq@c1": "1.0",
    }

    assert choose_cefr(row) == ("B1", 2.5)


def test_build_cache_creates_schema_metadata_and_skips_unusable_rows(tmp_path):
    tsv_path = tmp_path / "EFLLex_NLP4J"
    db_path = tmp_path / "efllex.sqlite"
    write_sample_tsv(tsv_path)

    inserted, skipped = build_cache(tsv_path, db_path)

    assert inserted == 4
    assert skipped == 3
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 4
        assert conn.execute(
            "SELECT value FROM metadata WHERE key = 'cefr_policy'"
        ).fetchone()[0] == "earliest_nonzero_level_frequency"
        assert conn.execute(
            "SELECT cefr FROM entries WHERE normalized_word = 'plausible'"
        ).fetchone()[0] == "B2"
        indexes = {
            row[1]
            for row in conn.execute("PRAGMA index_list(entries)").fetchall()
        }
        assert "idx_entries_word" in indexes
        assert "idx_entries_cefr" in indexes


def test_lookup_reads_best_entry_from_sqlite_cache(tmp_path):
    tsv_path = tmp_path / "EFLLex_NLP4J"
    db_path = tmp_path / "efllex.sqlite"
    write_sample_tsv(tsv_path)
    build_cache(tsv_path, db_path)

    lookup = CefrLookup(db_path)

    assert lookup.lookup(" plausible ") == {
        "word": "Plausible",
        "normalized_word": "plausible",
        "cefr": "B2",
        "tag": "JJ",
        "level_score": 0.3154,
        "total_freq": 0.045,
        "source": "EFLLex_NLP4J",
    }
    assert lookup.lookup("work")["tag"] == "VB"
    assert lookup.lookup("resilience") is None
    assert lookup.lookup("   ") is None


def test_lookup_is_singleton_and_uses_read_only_connection(tmp_path):
    tsv_path = tmp_path / "EFLLex_NLP4J"
    db_path = tmp_path / "efllex.sqlite"
    write_sample_tsv(tsv_path)
    build_cache(tsv_path, db_path)

    first = CefrLookup(db_path)
    second = CefrLookup(tmp_path / "different.sqlite")

    assert second is first
    assert second.db_path == db_path
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        first.conn.execute(
            "INSERT INTO metadata(key, value) VALUES ('should_fail', 'yes')"
        )
