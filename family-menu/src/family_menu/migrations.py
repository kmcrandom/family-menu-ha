from __future__ import annotations

import sqlite3


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS app_meta (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS preferences (
          id INTEGER PRIMARY KEY CHECK (id = 1),
          data TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS meals (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'active',
          likability INTEGER NOT NULL DEFAULT 80,
          active_prep_minutes INTEGER NOT NULL DEFAULT 20,
          cook_minutes INTEGER NOT NULL DEFAULT 20,
          make_ahead_score INTEGER NOT NULL DEFAULT 50,
          leftover_quality INTEGER NOT NULL DEFAULT 70,
          leftover_style TEXT NOT NULL DEFAULT 'mixed',
          tags TEXT NOT NULL DEFAULT '[]',
          diet_tags TEXT NOT NULL DEFAULT '[]',
          shared_ingredients TEXT NOT NULL DEFAULT '[]',
          primary_proteins TEXT NOT NULL DEFAULT '[]',
          alternate_proteins TEXT NOT NULL DEFAULT '[]',
          prep_ahead TEXT NOT NULL DEFAULT '[]',
          instructions TEXT NOT NULL DEFAULT '[]',
          source_url TEXT,
          source_name TEXT,
          simple_serving_variations TEXT NOT NULL DEFAULT '[]',
          notes TEXT,
          user_modified INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS variation_dimensions (
          id TEXT PRIMARY KEY,
          meal_id TEXT NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
          key TEXT NOT NULL,
          name TEXT NOT NULL,
          selection_mode TEXT NOT NULL DEFAULT 'single',
          required INTEGER NOT NULL DEFAULT 0,
          display_order INTEGER NOT NULL DEFAULT 0,
          status TEXT NOT NULL DEFAULT 'active',
          color TEXT,
          user_modified INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_variation_dimensions_meal
          ON variation_dimensions(meal_id, display_order);

        CREATE TABLE IF NOT EXISTS variation_options (
          id TEXT PRIMARY KEY,
          dimension_id TEXT NOT NULL REFERENCES variation_dimensions(id) ON DELETE CASCADE,
          meal_id TEXT NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
          name TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'active',
          likability INTEGER NOT NULL DEFAULT 80,
          value TEXT NOT NULL DEFAULT '{}',
          diet_tags TEXT NOT NULL DEFAULT '[]',
          compatible_diet_profiles TEXT NOT NULL DEFAULT '[]',
          ingredient_additions TEXT NOT NULL DEFAULT '[]',
          ingredient_omissions TEXT NOT NULL DEFAULT '[]',
          prep_ahead TEXT NOT NULL DEFAULT '[]',
          instructions TEXT NOT NULL DEFAULT '[]',
          tags TEXT NOT NULL DEFAULT '[]',
          overrides TEXT NOT NULL DEFAULT '{}',
          user_modified INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_variation_options_dimension
          ON variation_options(dimension_id);

        CREATE TABLE IF NOT EXISTS weekly_plans (
          id TEXT PRIMARY KEY,
          week_start_date TEXT NOT NULL UNIQUE,
          shopping_date TEXT NOT NULL,
          target_dinner_count INTEGER NOT NULL DEFAULT 5,
          status TEXT NOT NULL DEFAULT 'draft',
          notes TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS vacation_blocks (
          id TEXT PRIMARY KEY,
          weekly_plan_id TEXT NOT NULL REFERENCES weekly_plans(id) ON DELETE CASCADE,
          start_date TEXT NOT NULL,
          end_date TEXT NOT NULL,
          scope TEXT NOT NULL DEFAULT 'day',
          label TEXT NOT NULL DEFAULT 'Vacation',
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_vacation_blocks_plan
          ON vacation_blocks(weekly_plan_id, start_date, end_date);

        CREATE TABLE IF NOT EXISTS planned_meals (
          id TEXT PRIMARY KEY,
          weekly_plan_id TEXT NOT NULL REFERENCES weekly_plans(id) ON DELETE CASCADE,
          meal_id TEXT NOT NULL REFERENCES meals(id),
          variation_selections TEXT NOT NULL DEFAULT '{}',
          planned_date TEXT NOT NULL,
          position INTEGER NOT NULL,
          meal_slot TEXT NOT NULL DEFAULT 'dinner',
          servings_dinner INTEGER NOT NULL DEFAULT 4,
          leftover_lunch_servings INTEGER NOT NULL DEFAULT 2,
          locked INTEGER NOT NULL DEFAULT 0,
          variation_locks TEXT NOT NULL DEFAULT '{}',
          state TEXT NOT NULL DEFAULT 'planned',
          notes TEXT,
          recommendation_reasons TEXT NOT NULL DEFAULT '[]',
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_planned_meals_plan
          ON planned_meals(weekly_plan_id, position);

        CREATE TABLE IF NOT EXISTS meal_events (
          id TEXT PRIMARY KEY,
          meal_id TEXT NOT NULL REFERENCES meals(id),
          planned_meal_id TEXT REFERENCES planned_meals(id) ON DELETE SET NULL,
          eaten_date TEXT NOT NULL,
          variation_selections TEXT NOT NULL DEFAULT '{}',
          servings_dinner INTEGER NOT NULL DEFAULT 4,
          leftover_lunch_servings INTEGER NOT NULL DEFAULT 2,
          feedback TEXT,
          notes TEXT,
          created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_meal_events_meal_date
          ON meal_events(meal_id, eaten_date);

        CREATE TABLE IF NOT EXISTS checklist_items (
          id TEXT PRIMARY KEY,
          weekly_plan_id TEXT NOT NULL REFERENCES weekly_plans(id) ON DELETE CASCADE,
          kind TEXT NOT NULL,
          label TEXT NOT NULL,
          category TEXT,
          source TEXT,
          checked INTEGER NOT NULL DEFAULT 0,
          custom INTEGER NOT NULL DEFAULT 0,
          position INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS household_members (
          id TEXT PRIMARY KEY,
          display_name TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'active',
          dinner_servings REAL NOT NULL DEFAULT 1,
          leftover_lunch_servings REAL NOT NULL DEFAULT 0,
          dietary_profile_ids TEXT NOT NULL DEFAULT '[]',
          preference_tags TEXT NOT NULL DEFAULT '[]',
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS dietary_profiles (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          type TEXT NOT NULL DEFAULT 'custom',
          excluded_tags TEXT NOT NULL DEFAULT '[]',
          included_tags TEXT NOT NULL DEFAULT '[]',
          notes TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
        """
    )
    _ensure_columns(conn)
    conn.execute(
        "INSERT OR REPLACE INTO app_meta(key, value) VALUES ('schema_version', '4')"
    )
    conn.commit()


def _ensure_columns(conn: sqlite3.Connection) -> None:
    meal_columns = _table_columns(conn, "meals")
    _add_column_if_missing(conn, meal_columns, "meals", "diet_tags", "TEXT NOT NULL DEFAULT '[]'")
    _add_column_if_missing(conn, meal_columns, "meals", "alternate_proteins", "TEXT NOT NULL DEFAULT '[]'")
    _add_column_if_missing(conn, meal_columns, "meals", "simple_serving_variations", "TEXT NOT NULL DEFAULT '[]'")
    _add_column_if_missing(conn, meal_columns, "meals", "source_url", "TEXT")
    _add_column_if_missing(conn, meal_columns, "meals", "source_name", "TEXT")
    dimension_columns = _table_columns(conn, "variation_dimensions")
    _add_column_if_missing(conn, dimension_columns, "variation_dimensions", "color", "TEXT")
    option_columns = _table_columns(conn, "variation_options")
    _add_column_if_missing(conn, option_columns, "variation_options", "diet_tags", "TEXT NOT NULL DEFAULT '[]'")
    _add_column_if_missing(
        conn,
        option_columns,
        "variation_options",
        "compatible_diet_profiles",
        "TEXT NOT NULL DEFAULT '[]'",
    )
    updated_meal_columns = _table_columns(conn, "meals")
    legacy_alternate = "pescatarian" + "_proteins"
    legacy_simple = "k" + "id_variations"
    if legacy_alternate in updated_meal_columns:
        conn.execute(
            f"""
            UPDATE meals
            SET alternate_proteins = {legacy_alternate}
            WHERE alternate_proteins = '[]' AND {legacy_alternate} != '[]'
            """
        )
    if legacy_simple in updated_meal_columns:
        conn.execute(
            f"""
            UPDATE meals
            SET simple_serving_variations = {legacy_simple}
            WHERE simple_serving_variations = '[]' AND {legacy_simple} != '[]'
            """
        )


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def _add_column_if_missing(
    conn: sqlite3.Connection,
    columns: set[str],
    table: str,
    column: str,
    definition: str,
) -> None:
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
