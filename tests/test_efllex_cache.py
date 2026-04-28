from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_efllex_cache import build_cache, choose_cefr, normalize_word  # noqa: E402
from scripts.efllex_lookup import CefrLookup  # noqa: E402

REAL_SQLITE = ROOT / "references" / "efllex.sqlite"
VALID_CEFR_LEVELS = {"A1", "A2", "B1", "B2", "C1"}
EXPECTED_REAL_COUNTS = {
    "entries_rows": 15279,
    "distinct_words": 13869,
    "word_best_rows": 13869,
}
EXPECTED_REAL_CEFR_COUNTS = {
    "A1": 2395,
    "A2": 2478,
    "B1": 2739,
    "B2": 3934,
    "C1": 3733,
}


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
                "meat\tNN\t65.2524\t130.6943\t78.0931\t36.9111\t16.1182\t52.9129",
                "meat\t NN\t0\t0\t2.5892\t0\t0\t0.0865",
                "tie\tNN\t0\t2\t0\t0\t0\t10",
                "tie\tVB\t0\t2\t0\t0\t0\t10",
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

    assert inserted == 8
    assert skipped == 3
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 8
        assert conn.execute(
            "SELECT value FROM metadata WHERE key = 'cefr_policy'"
        ).fetchone()[0] == "earliest_nonzero_level_frequency"
        assert conn.execute(
            "SELECT cefr FROM entries WHERE normalized_word = 'plausible'"
        ).fetchone()[0] == "B2"
        assert conn.execute(
            "SELECT COUNT(*) FROM entries WHERE normalized_word = 'meat'"
        ).fetchone()[0] == 2
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
    assert lookup.lookup("meat")["cefr"] == "A1"
    assert lookup.lookup("tie")["tag"] == "NN"
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


def test_real_sqlite_cache_has_expected_full_dataset_counts():
    assert REAL_SQLITE.exists()

    with sqlite3.connect(REAL_SQLITE) as conn:
        actual_counts = {
            "entries_rows": conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0],
            "distinct_words": conn.execute(
                "SELECT COUNT(DISTINCT normalized_word) FROM entries"
            ).fetchone()[0],
            "word_best_rows": conn.execute("SELECT COUNT(*) FROM word_best").fetchone()[0],
        }
        duplicate_best_words = conn.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT normalized_word FROM word_best
                GROUP BY normalized_word
                HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]
        actual_cefr_counts = dict(
            conn.execute(
                "SELECT cefr, COUNT(*) FROM entries GROUP BY cefr ORDER BY cefr"
            ).fetchall()
        )
        metadata = dict(conn.execute("SELECT key, value FROM metadata").fetchall())

    assert actual_counts == EXPECTED_REAL_COUNTS
    assert actual_counts["word_best_rows"] == actual_counts["distinct_words"]
    assert duplicate_best_words == 0
    assert actual_cefr_counts == EXPECTED_REAL_CEFR_COUNTS
    assert metadata["inserted_rows"] == str(EXPECTED_REAL_COUNTS["entries_rows"])
    assert metadata["skipped_rows"] == "2"


def test_real_sqlite_cache_contains_only_valid_cefr_values_and_lookupable_words():
    lookup = CefrLookup(REAL_SQLITE)

    with sqlite3.connect(REAL_SQLITE) as conn:
        invalid_cefr_count = conn.execute(
            "SELECT COUNT(*) FROM entries WHERE cefr NOT IN ('A1', 'A2', 'B1', 'B2', 'C1')"
        ).fetchone()[0]
        nullish_count = conn.execute(
            """
            SELECT COUNT(*) FROM entries
            WHERE word = '' OR normalized_word = '' OR tag = '' OR cefr = ''
            """
        ).fetchone()[0]
        duplicate_entry_rows = conn.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT normalized_word, tag, cefr, level_score, total_freq
                FROM entries
                GROUP BY normalized_word, tag, cefr, level_score, total_freq
                HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]
        lookup_words = [
            row[0]
            for row in conn.execute(
                "SELECT DISTINCT normalized_word FROM word_best ORDER BY normalized_word"
            ).fetchall()
        ]

    assert invalid_cefr_count == 0
    assert nullish_count == 0
    assert duplicate_entry_rows == 0
    assert lookup_words

    for word in lookup_words:
        result = lookup.lookup(word)
        assert result is not None, word
        assert result["normalized_word"] == word
        assert result["cefr"] in VALID_CEFR_LEVELS


def test_real_sqlite_cache_known_fixture_words():
    lookup = CefrLookup(REAL_SQLITE)

    assert lookup.lookup("plausible")["cefr"] == "B2"
    assert lookup.lookup("the")["cefr"] == "A1"
    assert lookup.lookup("work")["cefr"] == "A1"
    assert lookup.lookup("meat")["cefr"] == "A1"
    assert lookup.lookup("resilience") is None
