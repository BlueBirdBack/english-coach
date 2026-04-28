#!/usr/bin/env python3
"""Read-only singleton EFLLex CEFR lookup helper.

Example:
    from scripts.efllex_lookup import CefrLookup
    print(CefrLookup().lookup("plausible"))
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock


class CefrLookup:
    """Process-level singleton that reuses one SQLite connection."""

    _instance: "CefrLookup | None" = None
    _lock = Lock()

    def __new__(cls, db_path: str | Path | None = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init(db_path)
            return cls._instance

    def _init(self, db_path: str | Path | None) -> None:
        if db_path is None:
            db_path = Path(__file__).resolve().parents[1] / "references" / "efllex.sqlite"
        self.db_path = Path(db_path)
        uri = f"file:{self.db_path}?mode=ro"
        self.conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    @staticmethod
    def normalize(word: str) -> str:
        return word.strip().replace("’", "'").lower()

    def lookup(self, word: str) -> dict[str, object] | None:
        normalized = self.normalize(word)
        if not normalized:
            return None
        row = self.conn.execute(
            """
            SELECT word, normalized_word, cefr, tag, level_score, total_freq, source
            FROM word_best
            WHERE normalized_word = ?
            ORDER BY total_freq DESC
            LIMIT 1
            """,
            (normalized,),
        ).fetchone()
        return dict(row) if row else None


if __name__ == "__main__":
    import sys

    lookup = CefrLookup()
    for item in sys.argv[1:] or ["plausible", "the", "resilience"]:
        print(item, "=>", lookup.lookup(item))
