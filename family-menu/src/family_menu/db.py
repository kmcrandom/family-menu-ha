from __future__ import annotations

import sqlite3
from pathlib import Path

from .migrations import init_db


def connect(path: Path | str) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


__all__ = ["connect", "init_db"]
