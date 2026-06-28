from __future__ import annotations

import sqlite3

from family_menu.migrations import init_db


def test_migration_adds_variation_dimension_color_to_existing_database():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(
            """
            CREATE TABLE variation_dimensions (
              id TEXT PRIMARY KEY,
              meal_id TEXT NOT NULL,
              key TEXT NOT NULL,
              name TEXT NOT NULL,
              selection_mode TEXT NOT NULL DEFAULT 'single',
              required INTEGER NOT NULL DEFAULT 0,
              display_order INTEGER NOT NULL DEFAULT 0,
              status TEXT NOT NULL DEFAULT 'active',
              user_modified INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            """
        )

        init_db(conn)

        columns = {row["name"] for row in conn.execute("PRAGMA table_info(variation_dimensions)")}
        assert "color" in columns
    finally:
        conn.close()
