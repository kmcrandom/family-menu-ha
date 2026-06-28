from __future__ import annotations

import json
import re
import sqlite3
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from fractions import Fraction
from pathlib import Path
from typing import Any

from .schemas import (
    DietaryProfileCreate,
    DietaryProfilePatch,
    HouseholdMemberCreate,
    HouseholdMemberPatch,
    HouseholdPatch,
    MealEventCreate,
    MealPatch,
    PlannedMealPatch,
    Preferences,
    VacationBlockCreate,
    VacationBlockPatch,
    VariationDimensionCreate,
    VariationDimensionPatch,
    VariationOptionCreate,
    VariationOptionPatch,
    normalize_ingredient_items,
)


JSON_FIELDS = {
    "tags",
    "diet_tags",
    "shared_ingredients",
    "primary_proteins",
    "alternate_proteins",
    "prep_ahead",
    "instructions",
    "simple_serving_variations",
    "value",
    "compatible_diet_profiles",
    "ingredient_additions",
    "ingredient_omissions",
    "overrides",
    "variation_selections",
    "variation_locks",
    "recommendation_reasons",
}


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def loads(value: str | None, fallback: Any) -> Any:
    if value in (None, ""):
        return fallback
    return json.loads(value)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def checklist_item_id(plan_id: str, kind: str, label: str) -> str:
    key = f"family-menu:{plan_id}:{kind}:{label.strip().lower()}"
    return f"check-{uuid.uuid5(uuid.NAMESPACE_URL, key).hex[:16]}"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or uuid.uuid4().hex[:8]


def row_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def meal_alternate_proteins(seed_meal: dict) -> list[str]:
    return seed_meal.get("alternate_proteins", seed_meal.get("pescatarian" + "_proteins", []))


def meal_simple_servings(seed_meal: dict) -> list[str]:
    return seed_meal.get("simple_serving_variations", seed_meal.get("k" + "id_variations", []))


def normalize_ingredient_item(value: Any) -> dict[str, str]:
    items = normalize_ingredient_items([value])
    return dict(items[0]) if items else {"label": ""}


def ingredient_label(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("label", "")).strip()
    return str(value).strip()


def ingredient_category_for(item: dict[str, Any]) -> str:
    return str(item.get("category") or ingredient_category(item["label"]))


def ingredient_amount_text(item: dict[str, Any]) -> str:
    amount = str(item.get("amount") or "").strip()
    unit = str(item.get("unit") or "").strip()
    if amount and unit:
        return f"{amount} {unit}"
    return amount or unit


def format_amount_value(value: float) -> str:
    if abs(value - round(value)) < 0.001:
        return str(int(round(value)))
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text


def parse_amount_value(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    parts = text.split()
    try:
        if len(parts) == 2 and "/" in parts[1]:
            return float(Fraction(parts[0]) + Fraction(parts[1]))
        if len(parts) == 1:
            return float(Fraction(parts[0]))
    except (ValueError, ZeroDivisionError):
        return None
    return None


UNIT_ALIASES: dict[str, tuple[str, str, float]] = {
    "g": ("weight", "g", 1.0),
    "gram": ("weight", "g", 1.0),
    "grams": ("weight", "g", 1.0),
    "oz": ("weight", "oz", 28.349523125),
    "ounce": ("weight", "oz", 28.349523125),
    "ounces": ("weight", "oz", 28.349523125),
    "lb": ("weight", "lb", 453.59237),
    "lbs": ("weight", "lb", 453.59237),
    "pound": ("weight", "lb", 453.59237),
    "pounds": ("weight", "lb", 453.59237),
    "ml": ("volume", "ml", 1.0),
    "milliliter": ("volume", "ml", 1.0),
    "milliliters": ("volume", "ml", 1.0),
    "l": ("volume", "l", 1000.0),
    "liter": ("volume", "l", 1000.0),
    "liters": ("volume", "l", 1000.0),
    "tsp": ("volume", "tsp", 4.92892159375),
    "teaspoon": ("volume", "tsp", 4.92892159375),
    "teaspoons": ("volume", "tsp", 4.92892159375),
    "tbsp": ("volume", "tbsp", 14.78676478125),
    "tablespoon": ("volume", "tbsp", 14.78676478125),
    "tablespoons": ("volume", "tbsp", 14.78676478125),
    "cup": ("volume", "cup", 236.5882365),
    "cups": ("volume", "cup", 236.5882365),
    "each": ("count", "each", 1.0),
    "ea": ("count", "each", 1.0),
    "count": ("count", "each", 1.0),
    "counts": ("count", "each", 1.0),
}


def parse_ingredient_amount(item: dict[str, Any]) -> dict[str, Any] | None:
    amount = parse_amount_value(item.get("amount"))
    if amount is None:
        return None
    raw_unit = str(item.get("unit") or "").strip().lower()
    if not raw_unit:
        return {"family": "count", "unit": "", "base": amount, "source_unit": ""}
    unit = UNIT_ALIASES.get(raw_unit)
    if unit is None:
        return None
    family, canonical_unit, factor = unit
    return {
        "family": family,
        "unit": canonical_unit,
        "base": amount * factor,
        "source_unit": canonical_unit,
    }


def format_summed_amount(contributions: list[dict[str, Any]]) -> tuple[str | None, str | None, str | None]:
    parsed = [item.get("parsed_amount") for item in contributions]
    if not parsed or any(item is None for item in parsed):
        return None, None, None
    families = {item["family"] for item in parsed}
    if len(families) != 1:
        return None, None, None
    family = families.pop()
    total = sum(item["base"] for item in parsed)
    source_units = {item["source_unit"] for item in parsed}
    if family == "count":
        amount = format_amount_value(total)
        return amount, None, amount
    if family == "weight":
        metric_only = source_units <= {"g"}
        if metric_only:
            amount = format_amount_value(total)
            return amount, "g", f"{amount} g"
        ounces = total / 28.349523125
        if ounces >= 16:
            amount = format_amount_value(total / 453.59237)
            return amount, "lb", f"{amount} lb"
        amount = format_amount_value(ounces)
        return amount, "oz", f"{amount} oz"
    if family == "volume":
        metric_only = source_units <= {"ml", "l"}
        if metric_only:
            if total >= 1000:
                amount = format_amount_value(total / 1000)
                return amount, "L", f"{amount} L"
            amount = format_amount_value(total)
            return amount, "mL", f"{amount} mL"
        cups = total / 236.5882365
        if cups >= 0.25:
            amount = format_amount_value(cups)
            return amount, "cups", f"{amount} cups"
        tbsp = total / 14.78676478125
        if tbsp >= 1:
            amount = format_amount_value(tbsp)
            return amount, "tbsp", f"{amount} tbsp"
        amount = format_amount_value(total / 4.92892159375)
        return amount, "tsp", f"{amount} tsp"
    return None, None, None


class Store:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def meal_count(self) -> int:
        row = self.conn.execute("SELECT count(*) AS count FROM meals").fetchone()
        return int(row["count"])

    def get_preferences(self) -> dict:
        row = self.conn.execute("SELECT data FROM preferences WHERE id = 1").fetchone()
        if row is None:
            prefs = Preferences().model_dump()
            self.set_preferences(prefs)
            return prefs
        stored = loads(row["data"], {})
        current = Preferences(**stored).model_dump()
        if current != stored:
            self.set_preferences(current)
        return current

    def set_preferences(self, values: dict) -> dict:
        current = Preferences(**values).model_dump()
        self.conn.execute(
            """
            INSERT INTO preferences(id, data, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
            """,
            (dumps(current), now_iso()),
        )
        self.conn.commit()
        return current

    def patch_preferences(self, values: dict) -> dict:
        current = self.get_preferences()
        current.update({key: value for key, value in values.items() if value is not None})
        return self.set_preferences(current)

    def household_config(self, database_path: str | None = None, seed_path: str | None = None) -> dict:
        self.ensure_default_household_config()
        return {
            "preferences": self.get_preferences(),
            "members": self.list_household_members(include_archived=True),
            "dietary_profiles": self.list_dietary_profiles(),
            "database_path": database_path,
            "seed_path": seed_path,
        }

    def ensure_default_household_config(self) -> None:
        timestamp = now_iso()
        if self.conn.execute("SELECT id FROM dietary_profiles LIMIT 1").fetchone() is None:
            self.conn.execute(
                """
                INSERT INTO dietary_profiles(
                  id, name, type, excluded_tags, included_tags, notes, created_at, updated_at
                )
                VALUES ('profile-omnivore', 'Omnivore', 'omnivore', '[]', '[]', NULL, ?, ?)
                """,
                (timestamp, timestamp),
            )
        if self.conn.execute("SELECT id FROM household_members LIMIT 1").fetchone() is None:
            self.conn.execute(
                """
                INSERT INTO household_members(
                  id, display_name, status, dinner_servings, leftover_lunch_servings,
                  dietary_profile_ids, preference_tags, created_at, updated_at
                )
                VALUES ('member-default', 'Eater 1', 'active', 1, 0, ?, '[]', ?, ?)
                """,
                (dumps(["profile-omnivore"]), timestamp, timestamp),
            )
        self.conn.commit()

    def list_household_members(self, include_archived: bool = False) -> list[dict]:
        query = "SELECT * FROM household_members"
        params: tuple[Any, ...] = ()
        if not include_archived:
            query += " WHERE status = ?"
            params = ("active",)
        query += " ORDER BY status, display_name"
        return [self._member_from_row(row) for row in self.conn.execute(query, params)]

    def create_household_member(self, payload: HouseholdMemberCreate) -> dict:
        timestamp = now_iso()
        member_id = new_id("member")
        self.conn.execute(
            """
            INSERT INTO household_members(
              id, display_name, status, dinner_servings, leftover_lunch_servings,
              dietary_profile_ids, preference_tags, created_at, updated_at
            )
            VALUES (?, ?, 'active', ?, ?, ?, ?, ?, ?)
            """,
            (
                member_id,
                payload.display_name,
                payload.dinner_servings,
                payload.leftover_lunch_servings,
                dumps(payload.dietary_profile_ids),
                dumps(payload.preference_tags),
                timestamp,
                timestamp,
            ),
        )
        self.conn.commit()
        return self.get_household_member(member_id)

    def get_household_member(self, member_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM household_members WHERE id = ?", (member_id,)).fetchone()
        if row is None:
            raise KeyError(member_id)
        return self._member_from_row(row)

    def patch_household_member(self, member_id: str, payload: HouseholdMemberPatch) -> dict:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return self.get_household_member(member_id)
        sets = []
        params: list[Any] = []
        for key, value in updates.items():
            if key in {"dietary_profile_ids", "preference_tags"}:
                value = dumps(value)
            sets.append(f"{key} = ?")
            params.append(value)
        sets.append("updated_at = ?")
        params.append(now_iso())
        params.append(member_id)
        cur = self.conn.execute(f"UPDATE household_members SET {', '.join(sets)} WHERE id = ?", params)
        if cur.rowcount == 0:
            raise KeyError(member_id)
        self.conn.commit()
        return self.get_household_member(member_id)

    def list_dietary_profiles(self) -> list[dict]:
        return [
            self._dietary_profile_from_row(row)
            for row in self.conn.execute("SELECT * FROM dietary_profiles ORDER BY name")
        ]

    def create_dietary_profile(self, payload: DietaryProfileCreate) -> dict:
        timestamp = now_iso()
        profile_id = f"profile-{slugify(payload.name)}"
        self.conn.execute(
            """
            INSERT INTO dietary_profiles(
              id, name, type, excluded_tags, included_tags, notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile_id,
                payload.name,
                payload.type,
                dumps(payload.excluded_tags),
                dumps(payload.included_tags),
                payload.notes,
                timestamp,
                timestamp,
            ),
        )
        self.conn.commit()
        return self.get_dietary_profile(profile_id)

    def get_dietary_profile(self, profile_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM dietary_profiles WHERE id = ?", (profile_id,)).fetchone()
        if row is None:
            raise KeyError(profile_id)
        return self._dietary_profile_from_row(row)

    def patch_dietary_profile(self, profile_id: str, payload: DietaryProfilePatch) -> dict:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return self.get_dietary_profile(profile_id)
        sets = []
        params: list[Any] = []
        for key, value in updates.items():
            if key in {"excluded_tags", "included_tags"}:
                value = dumps(value)
            sets.append(f"{key} = ?")
            params.append(value)
        sets.append("updated_at = ?")
        params.append(now_iso())
        params.append(profile_id)
        cur = self.conn.execute(f"UPDATE dietary_profiles SET {', '.join(sets)} WHERE id = ?", params)
        if cur.rowcount == 0:
            raise KeyError(profile_id)
        self.conn.commit()
        return self.get_dietary_profile(profile_id)

    def patch_household(self, payload: HouseholdPatch) -> dict:
        updates = payload.model_dump(exclude_unset=True)
        if updates:
            self.patch_preferences(updates)
        return self.household_config()

    def _member_from_row(self, row: sqlite3.Row) -> dict:
        member = row_dict(row)
        member["dietary_profile_ids"] = loads(member["dietary_profile_ids"], [])
        member["preference_tags"] = loads(member["preference_tags"], [])
        return member

    def _dietary_profile_from_row(self, row: sqlite3.Row) -> dict:
        profile = row_dict(row)
        profile["excluded_tags"] = loads(profile["excluded_tags"], [])
        profile["included_tags"] = loads(profile["included_tags"], [])
        return profile

    def import_seed(self, path: Path, overwrite: bool = False) -> dict:
        data = json.loads(path.read_text())
        created = {"meals": 0, "dimensions": 0, "options": 0}
        timestamp = now_iso()
        for meal in data["meals"]:
            meal_exists = self.conn.execute("SELECT id FROM meals WHERE id = ?", (meal["id"],)).fetchone()
            if meal_exists is None or overwrite:
                self.conn.execute(
                    """
                    INSERT INTO meals(
                      id, name, status, likability, active_prep_minutes, cook_minutes,
                      make_ahead_score, leftover_quality, leftover_style, tags,
                      diet_tags, shared_ingredients, primary_proteins, alternate_proteins,
                      prep_ahead, instructions, source_url, source_name,
                      simple_serving_variations, notes, user_modified,
                      created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                      name = CASE WHEN meals.user_modified = 0 OR ? THEN excluded.name ELSE meals.name END,
                      status = excluded.status,
                      updated_at = excluded.updated_at
                    """,
                    (
                        meal["id"],
                        meal["name"],
                        meal.get("status", "active"),
                        meal.get("likability", 80),
                        meal.get("active_prep_minutes", 20),
                        meal.get("cook_minutes", 20),
                        meal.get("make_ahead_score", 50),
                        meal.get("leftover_quality", 70),
                        meal.get("leftover_style", "mixed"),
                        dumps(meal.get("tags", [])),
                        dumps(meal.get("diet_tags", [])),
                        dumps(normalize_ingredient_items(meal.get("shared_ingredients", []))),
                        dumps(meal.get("primary_proteins", [])),
                        dumps(meal_alternate_proteins(meal)),
                        dumps(meal.get("prep_ahead", [])),
                        dumps(meal.get("instructions", [])),
                        meal.get("source_url"),
                        meal.get("source_name"),
                        dumps(meal_simple_servings(meal)),
                        meal.get("notes"),
                        timestamp,
                        timestamp,
                        1 if overwrite else 0,
                    ),
                )
                if meal_exists is None:
                    created["meals"] += 1
            for index, dimension in enumerate(meal.get("variation_dimensions", [])):
                dim_exists = self.conn.execute(
                    "SELECT id FROM variation_dimensions WHERE id = ?", (dimension["id"],)
                ).fetchone()
                if dim_exists is None or overwrite:
                    self.conn.execute(
                        """
                        INSERT INTO variation_dimensions(
                          id, meal_id, key, name, selection_mode, required, display_order,
                          status, color, user_modified, created_at, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                          name = CASE WHEN variation_dimensions.user_modified = 0 OR ? THEN excluded.name ELSE variation_dimensions.name END,
                          status = excluded.status,
                          color = CASE WHEN variation_dimensions.user_modified = 0 OR ? THEN excluded.color ELSE variation_dimensions.color END,
                          updated_at = excluded.updated_at
                        """,
                        (
                            dimension["id"],
                            meal["id"],
                            dimension["key"],
                            dimension["name"],
                            dimension.get("selection_mode", "single"),
                            1 if dimension.get("required") else 0,
                            dimension.get("display_order", index),
                            dimension.get("status", "active"),
                            dimension.get("color"),
                            timestamp,
                            timestamp,
                            1 if overwrite else 0,
                            1 if overwrite else 0,
                        ),
                    )
                    if dim_exists is None:
                        created["dimensions"] += 1
                for option in dimension.get("options", []):
                    opt_exists = self.conn.execute(
                        "SELECT id FROM variation_options WHERE id = ?", (option["id"],)
                    ).fetchone()
                    if opt_exists is None or overwrite:
                        self.conn.execute(
                            """
                            INSERT INTO variation_options(
                              id, dimension_id, meal_id, name, status, likability, value,
                              diet_tags, compatible_diet_profiles,
                              ingredient_additions, ingredient_omissions, prep_ahead,
                              instructions, tags, overrides, user_modified, created_at, updated_at
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                            ON CONFLICT(id) DO UPDATE SET
                              name = CASE WHEN variation_options.user_modified = 0 OR ? THEN excluded.name ELSE variation_options.name END,
                              status = excluded.status,
                              updated_at = excluded.updated_at
                            """,
                            (
                                option["id"],
                                dimension["id"],
                                meal["id"],
                                option["name"],
                                option.get("status", "active"),
                                option.get("likability", 80),
                                dumps(option.get("value", {})),
                                dumps(option.get("diet_tags", [])),
                                dumps(option.get("compatible_diet_profiles", [])),
                                dumps(normalize_ingredient_items(option.get("ingredient_additions", []))),
                                dumps(option.get("ingredient_omissions", [])),
                                dumps(option.get("prep_ahead", [])),
                                dumps(option.get("instructions", [])),
                                dumps(option.get("tags", [])),
                                dumps(option.get("overrides", {})),
                                timestamp,
                                timestamp,
                                1 if overwrite else 0,
                            ),
                        )
                        if opt_exists is None:
                            created["options"] += 1
        if self.conn.execute("SELECT id FROM preferences WHERE id = 1").fetchone() is None:
            self.set_preferences(Preferences().model_dump())
        self.conn.commit()
        return created

    def list_meals(self, include_archived: bool = False) -> list[dict]:
        query = "SELECT * FROM meals"
        params: tuple[Any, ...] = ()
        if not include_archived:
            query += " WHERE status = ?"
            params = ("active",)
        query += " ORDER BY status, name"
        return [
            self.meal_response(row["id"], include_archived_options=include_archived)
            for row in self.conn.execute(query, params)
        ]

    def meal_response(self, meal_id: str, include_archived_options: bool = True) -> dict:
        row = self.conn.execute("SELECT * FROM meals WHERE id = ?", (meal_id,)).fetchone()
        if row is None:
            raise KeyError(meal_id)
        meal = self._meal_from_row(row)
        meal["variation_dimensions"] = self.list_dimensions(meal_id, include_archived=include_archived_options)
        return meal

    def _meal_from_row(self, row: sqlite3.Row) -> dict:
        meal = row_dict(row)
        for key in [
            "tags",
            "diet_tags",
            "shared_ingredients",
            "primary_proteins",
            "alternate_proteins",
            "prep_ahead",
            "instructions",
            "simple_serving_variations",
        ]:
            meal[key] = loads(meal[key], [])
        meal["source_url"] = meal.get("source_url") or None
        meal["source_name"] = meal.get("source_name") or None
        meal["shared_ingredients"] = normalize_ingredient_items(meal["shared_ingredients"])
        meal.pop("pescatarian" + "_proteins", None)
        meal.pop("k" + "id_variations", None)
        meal.pop("user_modified", None)
        return meal

    def patch_meal(self, meal_id: str, payload: MealPatch) -> dict:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return self.meal_response(meal_id)
        sets = []
        params: list[Any] = []
        for key, value in updates.items():
            if key in JSON_FIELDS:
                value = dumps(value)
            sets.append(f"{key} = ?")
            params.append(value)
        sets.extend(["user_modified = 1", "updated_at = ?"])
        params.append(now_iso())
        params.append(meal_id)
        cur = self.conn.execute(f"UPDATE meals SET {', '.join(sets)} WHERE id = ?", params)
        if cur.rowcount == 0:
            raise KeyError(meal_id)
        self.conn.commit()
        return self.meal_response(meal_id)

    def set_meal_status(self, meal_id: str, status: str) -> dict:
        cur = self.conn.execute(
            "UPDATE meals SET status = ?, user_modified = 1, updated_at = ? WHERE id = ?",
            (status, now_iso(), meal_id),
        )
        if cur.rowcount == 0:
            raise KeyError(meal_id)
        self.conn.commit()
        return self.meal_response(meal_id)

    def list_dimensions(self, meal_id: str, include_archived: bool = False) -> list[dict]:
        query = "SELECT * FROM variation_dimensions WHERE meal_id = ?"
        params: list[Any] = [meal_id]
        if not include_archived:
            query += " AND status = ?"
            params.append("active")
        query += " ORDER BY display_order, name"
        dimensions = []
        for row in self.conn.execute(query, params):
            dimension = row_dict(row)
            dimension["required"] = bool(dimension["required"])
            dimension.pop("user_modified", None)
            dimension["options"] = self.list_options(dimension["id"], include_archived=include_archived)
            dimensions.append(dimension)
        return dimensions

    def list_options(self, dimension_id: str, include_archived: bool = False) -> list[dict]:
        query = "SELECT * FROM variation_options WHERE dimension_id = ?"
        params: list[Any] = [dimension_id]
        if not include_archived:
            query += " AND status = ?"
            params.append("active")
        query += " ORDER BY likability DESC, name"
        options = []
        for row in self.conn.execute(query, params):
            option = row_dict(row)
            for key in [
                "value",
                "diet_tags",
                "compatible_diet_profiles",
                "ingredient_additions",
                "ingredient_omissions",
                "prep_ahead",
                "instructions",
                "tags",
                "overrides",
            ]:
                option[key] = loads(option[key], {} if key in {"value", "overrides"} else [])
            option["ingredient_additions"] = normalize_ingredient_items(option["ingredient_additions"])
            option.pop("user_modified", None)
            options.append(option)
        return options

    def create_dimension(self, meal_id: str, payload: VariationDimensionCreate) -> dict:
        self.meal_response(meal_id)
        timestamp = now_iso()
        dimension_id = f"{meal_id}-{slugify(payload.key.replace('variation_', ''))}"
        existing = self.conn.execute(
            "SELECT id, status FROM variation_dimensions WHERE id = ?",
            (dimension_id,),
        ).fetchone()
        if existing is not None:
            if existing["status"] == "archived":
                return self.patch_dimension(
                    dimension_id,
                    VariationDimensionPatch(
                        key=payload.key,
                        name=payload.name,
                        selection_mode=payload.selection_mode,
                        required=payload.required,
                        display_order=payload.display_order,
                        status="active",
                        color=payload.color,
                    ),
                )
            raise ValueError(f"Variation dimension already exists: {payload.name}")
        self.conn.execute(
            """
            INSERT INTO variation_dimensions(
              id, meal_id, key, name, selection_mode, required, display_order,
              status, color, user_modified, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, 1, ?, ?)
            """,
            (
                dimension_id,
                meal_id,
                payload.key,
                payload.name,
                payload.selection_mode,
                1 if payload.required else 0,
                payload.display_order,
                payload.color,
                timestamp,
                timestamp,
            ),
        )
        self.conn.commit()
        return self.get_dimension(dimension_id)

    def get_dimension(self, dimension_id: str, include_archived: bool = True) -> dict:
        row = self.conn.execute("SELECT * FROM variation_dimensions WHERE id = ?", (dimension_id,)).fetchone()
        if row is None:
            raise KeyError(dimension_id)
        dimension = row_dict(row)
        dimension["required"] = bool(dimension["required"])
        dimension.pop("user_modified", None)
        dimension["options"] = self.list_options(dimension_id, include_archived=include_archived)
        return dimension

    def patch_dimension(self, dimension_id: str, payload: VariationDimensionPatch) -> dict:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return self.get_dimension(dimension_id)
        sets = []
        params: list[Any] = []
        for key, value in updates.items():
            if key == "required":
                value = 1 if value else 0
            sets.append(f"{key} = ?")
            params.append(value)
        sets.extend(["user_modified = 1", "updated_at = ?"])
        params.append(now_iso())
        params.append(dimension_id)
        cur = self.conn.execute(f"UPDATE variation_dimensions SET {', '.join(sets)} WHERE id = ?", params)
        if cur.rowcount == 0:
            raise KeyError(dimension_id)
        self.conn.commit()
        return self.get_dimension(dimension_id)

    def create_option(self, dimension_id: str, payload: VariationOptionCreate) -> dict:
        dimension = self.get_dimension(dimension_id)
        option_id = f"{dimension_id}-{slugify(payload.name)}"
        timestamp = now_iso()
        self.conn.execute(
            """
            INSERT INTO variation_options(
              id, dimension_id, meal_id, name, status, likability, value,
              diet_tags, compatible_diet_profiles, ingredient_additions,
              ingredient_omissions, prep_ahead, instructions, tags, overrides,
              user_modified, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                option_id,
                dimension_id,
                dimension["meal_id"],
                payload.name,
                payload.likability,
                dumps(payload.value),
                dumps(payload.diet_tags),
                dumps(payload.compatible_diet_profiles),
                dumps(normalize_ingredient_items(payload.model_dump()["ingredient_additions"])),
                dumps(payload.ingredient_omissions),
                dumps(payload.prep_ahead),
                dumps(payload.instructions),
                dumps(payload.tags),
                dumps(payload.overrides),
                timestamp,
                timestamp,
            ),
        )
        self.conn.commit()
        return self.get_option(option_id)

    def get_option(self, option_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM variation_options WHERE id = ?", (option_id,)).fetchone()
        if row is None:
            raise KeyError(option_id)
        option = row_dict(row)
        for key in [
            "value",
            "diet_tags",
            "compatible_diet_profiles",
            "ingredient_additions",
            "ingredient_omissions",
            "prep_ahead",
            "instructions",
            "tags",
            "overrides",
        ]:
            option[key] = loads(option[key], {} if key in {"value", "overrides"} else [])
        option["ingredient_additions"] = normalize_ingredient_items(option["ingredient_additions"])
        option.pop("user_modified", None)
        return option

    def patch_option(self, option_id: str, payload: VariationOptionPatch) -> dict:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return self.get_option(option_id)
        sets = []
        params: list[Any] = []
        for key, value in updates.items():
            if key in JSON_FIELDS:
                value = dumps(value)
            sets.append(f"{key} = ?")
            params.append(value)
        sets.extend(["user_modified = 1", "updated_at = ?"])
        params.append(now_iso())
        params.append(option_id)
        cur = self.conn.execute(f"UPDATE variation_options SET {', '.join(sets)} WHERE id = ?", params)
        if cur.rowcount == 0:
            raise KeyError(option_id)
        self.conn.commit()
        return self.get_option(option_id)

    def set_option_status(self, option_id: str, status: str) -> dict:
        cur = self.conn.execute(
            "UPDATE variation_options SET status = ?, user_modified = 1, updated_at = ? WHERE id = ?",
            (status, now_iso(), option_id),
        )
        if cur.rowcount == 0:
            raise KeyError(option_id)
        self.conn.commit()
        return self.get_option(option_id)

    def current_week_start(self, today: date | None = None) -> date:
        today = today or date.today()
        # Preferences currently support Sunday start. This is intentionally simple for v1.
        days_since_sunday = (today.weekday() + 1) % 7
        return today - timedelta(days=days_since_sunday)

    def get_or_create_plan(self, week_start_date: date | None = None) -> dict:
        prefs = self.get_preferences()
        week_start_date = week_start_date or self.current_week_start()
        plan = self.get_plan_by_week(week_start_date)
        if plan is not None:
            return plan
        timestamp = now_iso()
        plan_id = f"plan-{week_start_date.isoformat()}"
        self.conn.execute(
            """
            INSERT INTO weekly_plans(
              id, week_start_date, shopping_date, target_dinner_count, status, notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, 'draft', NULL, ?, ?)
            """,
            (
                plan_id,
                week_start_date.isoformat(),
                week_start_date.isoformat(),
                prefs["default_week_size"],
                timestamp,
                timestamp,
            ),
        )
        self.conn.commit()
        return self.plan_response(plan_id)

    def get_plan_by_week(self, week_start_date: date) -> dict | None:
        row = self.conn.execute(
            "SELECT id FROM weekly_plans WHERE week_start_date = ?", (week_start_date.isoformat(),)
        ).fetchone()
        if row is None:
            return None
        return self.plan_response(row["id"])

    def plan_response(self, plan_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM weekly_plans WHERE id = ?", (plan_id,)).fetchone()
        if row is None:
            raise KeyError(plan_id)
        plan = row_dict(row)
        plan["vacation_blocks"] = self.list_vacation_blocks(plan_id)
        plan["planned_meals"] = self.list_planned_meals(plan_id)
        return plan

    def list_vacation_blocks(self, plan_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM vacation_blocks WHERE weekly_plan_id = ? ORDER BY start_date, end_date, created_at",
            (plan_id,),
        )
        return [row_dict(row) for row in rows]

    def get_vacation_block(self, block_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM vacation_blocks WHERE id = ?", (block_id,)).fetchone()
        if row is None:
            raise KeyError(block_id)
        return row_dict(row)

    def create_vacation_block(self, plan_id: str, payload: VacationBlockCreate) -> dict:
        plan = self.plan_response(plan_id)
        start_date, end_date = self.vacation_block_dates(plan, payload.start_date, payload.end_date, payload.scope)
        timestamp = now_iso()
        block_id = new_id("vacation")
        self.conn.execute(
            """
            INSERT INTO vacation_blocks(
              id, weekly_plan_id, start_date, end_date, scope, label, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                block_id,
                plan_id,
                start_date.isoformat(),
                end_date.isoformat(),
                payload.scope,
                payload.label,
                timestamp,
                timestamp,
            ),
        )
        self.delete_planned_meals_between(plan_id, start_date, end_date)
        self.conn.execute("UPDATE weekly_plans SET updated_at = ? WHERE id = ?", (timestamp, plan_id))
        self.conn.commit()
        return self.plan_response(plan_id)

    def patch_vacation_block(self, block_id: str, payload: VacationBlockPatch) -> dict:
        existing = self.get_vacation_block(block_id)
        plan = self.plan_response(existing["weekly_plan_id"])
        updates = payload.model_dump(exclude_unset=True)
        scope = updates.get("scope", existing["scope"])
        input_start = updates.get("start_date") or date.fromisoformat(existing["start_date"])
        input_end = updates.get("end_date")
        if input_end is None and "end_date" not in updates:
            input_end = date.fromisoformat(existing["end_date"])
        start_date, end_date = self.vacation_block_dates(plan, input_start, input_end, scope)
        label = updates.get("label", existing["label"])
        timestamp = now_iso()
        self.conn.execute(
            """
            UPDATE vacation_blocks
            SET start_date = ?, end_date = ?, scope = ?, label = ?, updated_at = ?
            WHERE id = ?
            """,
            (start_date.isoformat(), end_date.isoformat(), scope, label, timestamp, block_id),
        )
        self.delete_planned_meals_between(existing["weekly_plan_id"], start_date, end_date)
        self.conn.execute(
            "UPDATE weekly_plans SET updated_at = ? WHERE id = ?",
            (timestamp, existing["weekly_plan_id"]),
        )
        self.conn.commit()
        return self.plan_response(existing["weekly_plan_id"])

    def delete_vacation_block(self, block_id: str) -> dict:
        existing = self.get_vacation_block(block_id)
        timestamp = now_iso()
        self.conn.execute("DELETE FROM vacation_blocks WHERE id = ?", (block_id,))
        self.conn.execute(
            "UPDATE weekly_plans SET updated_at = ? WHERE id = ?",
            (timestamp, existing["weekly_plan_id"]),
        )
        self.conn.commit()
        return self.plan_response(existing["weekly_plan_id"])

    def vacation_block_dates(
        self,
        plan: dict,
        start_date: date,
        end_date: date | None,
        scope: str,
    ) -> tuple[date, date]:
        week_start = date.fromisoformat(plan["week_start_date"])
        if scope == "week":
            return week_start, week_start + timedelta(days=6)
        end = end_date or start_date
        if end < start_date:
            raise ValueError("Vacation end date cannot be before start date.")
        return start_date, end

    def delete_planned_meals_between(self, plan_id: str, start_date: date, end_date: date) -> None:
        self.conn.execute(
            """
            DELETE FROM planned_meals
            WHERE weekly_plan_id = ?
              AND planned_date >= ?
              AND planned_date <= ?
            """,
            (plan_id, start_date.isoformat(), end_date.isoformat()),
        )

    def list_planned_meals(self, plan_id: str) -> list[dict]:
        meals = []
        for row in self.conn.execute(
            "SELECT * FROM planned_meals WHERE weekly_plan_id = ? ORDER BY position, planned_date",
            (plan_id,),
        ):
            planned = row_dict(row)
            planned["variation_selections"] = loads(planned["variation_selections"], {})
            planned["variation_locks"] = loads(planned["variation_locks"], {})
            planned["recommendation_reasons"] = loads(planned["recommendation_reasons"], [])
            planned["locked"] = bool(planned["locked"])
            planned["meal"] = self.meal_response(planned["meal_id"], include_archived_options=True)
            meals.append(planned)
        return meals

    def create_planned_meal(
        self,
        plan_id: str,
        meal_id: str,
        planned_date: date,
        position: int,
        variation_selections: dict[str, str] | None = None,
        reasons: list[str] | None = None,
    ) -> dict:
        plan = self.plan_response(plan_id)
        self.meal_response(meal_id)
        timestamp = now_iso()
        planned_id = new_id("planned")
        prefs = self.get_preferences()
        self.conn.execute(
            """
            INSERT INTO planned_meals(
              id, weekly_plan_id, meal_id, variation_selections, planned_date, position,
              meal_slot, servings_dinner, leftover_lunch_servings, locked, variation_locks,
              state, notes, recommendation_reasons, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'dinner', ?, ?, 0, '{}', 'planned', NULL, ?, ?, ?)
            """,
            (
                planned_id,
                plan_id,
                meal_id,
                dumps(variation_selections or {}),
                planned_date.isoformat(),
                position,
                prefs["default_dinner_servings"],
                prefs["default_leftover_lunch_servings"],
                dumps(reasons or []),
                timestamp,
                timestamp,
            ),
        )
        self.conn.execute(
            "UPDATE weekly_plans SET status = 'planned', updated_at = ? WHERE id = ?",
            (timestamp, plan["id"]),
        )
        self.conn.commit()
        return self.planned_meal_response(planned_id)

    def planned_meal_response(self, planned_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM planned_meals WHERE id = ?", (planned_id,)).fetchone()
        if row is None:
            raise KeyError(planned_id)
        planned = row_dict(row)
        planned["variation_selections"] = loads(planned["variation_selections"], {})
        planned["variation_locks"] = loads(planned["variation_locks"], {})
        planned["recommendation_reasons"] = loads(planned["recommendation_reasons"], [])
        planned["locked"] = bool(planned["locked"])
        planned["meal"] = self.meal_response(planned["meal_id"], include_archived_options=True)
        return planned

    def patch_planned_meal(self, planned_id: str, payload: PlannedMealPatch) -> dict:
        existing = self.planned_meal_response(planned_id)
        updates = payload.model_dump(exclude_unset=True)
        if "meal_id" in updates and updates["meal_id"] != existing["meal_id"]:
            updates.setdefault("variation_selections", self.default_variation_selections(updates["meal_id"]))
            updates.setdefault("variation_locks", {})
            updates.setdefault("recommendation_reasons", ["manual_replacement"])
        sets = []
        params: list[Any] = []
        for key, value in updates.items():
            if key in {"variation_selections", "variation_locks", "recommendation_reasons"}:
                value = dumps(value)
            elif isinstance(value, date):
                value = value.isoformat()
            elif key == "locked":
                value = 1 if value else 0
            sets.append(f"{key} = ?")
            params.append(value)
        if not sets:
            return existing
        sets.append("updated_at = ?")
        params.append(now_iso())
        params.append(planned_id)
        self.conn.execute(f"UPDATE planned_meals SET {', '.join(sets)} WHERE id = ?", params)
        self.conn.commit()
        return self.planned_meal_response(planned_id)

    def vacation_blocked_dates(self, plan_id: str) -> set[date]:
        blocked: set[date] = set()
        for block in self.list_vacation_blocks(plan_id):
            current = date.fromisoformat(block["start_date"])
            end = date.fromisoformat(block["end_date"])
            while current <= end:
                blocked.add(current)
                current += timedelta(days=1)
        return blocked

    def replace_plan_unlocked(self, plan_id: str, selections: list[dict], blocked_dates: set[date] | None = None) -> dict:
        existing = self.list_planned_meals(plan_id)
        locked_by_position = {item["position"]: item for item in existing if item["locked"]}
        timestamp = now_iso()
        if blocked_dates:
            placeholders = ",".join("?" for _ in blocked_dates)
            params: list[Any] = [plan_id, *sorted(item.isoformat() for item in blocked_dates)]
            self.conn.execute(
                f"DELETE FROM planned_meals WHERE weekly_plan_id = ? AND planned_date IN ({placeholders})",
                params,
            )
            locked_by_position = {
                position: item
                for position, item in locked_by_position.items()
                if date.fromisoformat(item["planned_date"]) not in blocked_dates
            }
        self.conn.execute("DELETE FROM planned_meals WHERE weekly_plan_id = ? AND locked = 0", (plan_id,))
        for selection in selections:
            if blocked_dates and selection["planned_date"] in blocked_dates:
                continue
            if selection["position"] in locked_by_position:
                continue
            self.create_planned_meal(
                plan_id,
                selection["meal_id"],
                selection["planned_date"],
                selection["position"],
                selection["variation_selections"],
                selection["reasons"],
            )
        self.conn.execute("UPDATE weekly_plans SET status = 'planned', updated_at = ? WHERE id = ?", (timestamp, plan_id))
        self.conn.commit()
        return self.plan_response(plan_id)

    def default_variation_selections(self, meal_id: str) -> dict[str, str]:
        selections: dict[str, str] = {}
        for dimension in self.list_dimensions(meal_id, include_archived=False):
            options = dimension["options"]
            if options:
                selections[dimension["id"]] = options[0]["id"]
        return selections

    def create_event_from_planned(self, planned_id: str, feedback: str | None = None) -> dict:
        planned = self.planned_meal_response(planned_id)
        payload = MealEventCreate(
            meal_id=planned["meal_id"],
            planned_meal_id=planned["id"],
            eaten_date=date.fromisoformat(planned["planned_date"]),
            variation_selections=planned["variation_selections"],
            servings_dinner=planned["servings_dinner"],
            leftover_lunch_servings=planned["leftover_lunch_servings"],
            feedback=feedback,
        )
        event = self.create_event(payload)
        self.patch_planned_meal(planned_id, PlannedMealPatch(state="eaten"))
        return event

    def create_event(self, payload: MealEventCreate) -> dict:
        self.meal_response(payload.meal_id)
        timestamp = now_iso()
        event_id = new_id("event")
        self.conn.execute(
            """
            INSERT INTO meal_events(
              id, meal_id, planned_meal_id, eaten_date, variation_selections,
              servings_dinner, leftover_lunch_servings, feedback, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                payload.meal_id,
                payload.planned_meal_id,
                payload.eaten_date.isoformat(),
                dumps(payload.variation_selections),
                payload.servings_dinner,
                payload.leftover_lunch_servings,
                payload.feedback,
                payload.notes,
                timestamp,
            ),
        )
        self.conn.commit()
        return self.event_response(event_id)

    def event_response(self, event_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM meal_events WHERE id = ?", (event_id,)).fetchone()
        if row is None:
            raise KeyError(event_id)
        event = row_dict(row)
        event["variation_selections"] = loads(event["variation_selections"], {})
        event["meal"] = self.meal_response(event["meal_id"], include_archived_options=True)
        return event

    def list_events(self, limit: int = 200) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id FROM meal_events ORDER BY eaten_date DESC, created_at DESC LIMIT ?",
            (limit,),
        )
        return [self.event_response(row["id"]) for row in rows]

    def delete_event(self, event_id: str) -> None:
        self.conn.execute("DELETE FROM meal_events WHERE id = ?", (event_id,))
        self.conn.commit()

    def meal_history_stats(self) -> dict:
        events = self.list_events(limit=10000)
        meal_counts = Counter(event["meal_id"] for event in events)
        option_counts: Counter[str] = Counter()
        last_meal: dict[str, date] = {}
        last_option: dict[str, date] = {}
        for event in events:
            eaten_date = date.fromisoformat(event["eaten_date"])
            last_meal[event["meal_id"]] = max(last_meal.get(event["meal_id"], eaten_date), eaten_date)
            for option_id in event["variation_selections"].values():
                option_counts[option_id] += 1
                last_option[option_id] = max(last_option.get(option_id, eaten_date), eaten_date)
        return {
            "events": events,
            "meal_counts": meal_counts,
            "option_counts": option_counts,
            "last_meal": last_meal,
            "last_option": last_option,
        }

    def grocery_prep(self, plan_id: str) -> dict:
        plan = self.plan_response(plan_id)
        grocery: dict[str, dict] = {}
        prep: dict[str, dict] = {}

        def add_checklist(target: dict[str, dict], label: str, source: str, category: str = "General") -> None:
            key = label.strip().lower()
            if not key:
                return
            if key not in target:
                target[key] = {"label": label, "category": category, "source": source, "checked": False}
            elif source not in target[key]["source"]:
                target[key]["source"] += f", {source}"

        def add_grocery(raw_ingredient: Any, source: str) -> None:
            ingredient = normalize_ingredient_item(raw_ingredient)
            label = ingredient_label(ingredient)
            key = label.strip().lower()
            if not key:
                return
            contribution = {
                "source": source,
                "amount_text": ingredient_amount_text(ingredient),
                "parsed_amount": parse_ingredient_amount(ingredient),
            }
            if key not in grocery:
                grocery[key] = {
                    "label": label,
                    "category": ingredient_category_for(ingredient),
                    "source": source,
                    "checked": False,
                    "_contributions": [contribution],
                }
            else:
                if source not in grocery[key]["source"]:
                    grocery[key]["source"] += f", {source}"
                grocery[key]["_contributions"].append(contribution)

        for planned in plan["planned_meals"]:
            meal = planned["meal"]
            meal_name = meal["name"]
            selected_options = self.options_by_id(planned["variation_selections"].values())
            omitted_ingredients = {
                ingredient_label(ingredient).lower()
                for option in selected_options.values()
                for ingredient in option.get("ingredient_omissions", [])
                if ingredient_label(ingredient)
            }
            for ingredient in meal["shared_ingredients"]:
                if ingredient_label(ingredient).lower() in omitted_ingredients:
                    continue
                add_grocery(ingredient, meal_name)
            for task in meal["prep_ahead"]:
                add_checklist(prep, task, meal_name, "Sunday prep")
            for option in selected_options.values():
                source = f"{meal_name}: {option['name']}"
                for ingredient in option.get("ingredient_additions", []):
                    add_grocery(ingredient, source)
                value = option.get("value", {})
                if isinstance(value, dict):
                    for v in value.values():
                        add_grocery(str(v), source)
                elif isinstance(value, list):
                    for v in value:
                        add_grocery(str(v), source)
                for task in option.get("prep_ahead", []):
                    add_checklist(prep, task, source, "Sunday prep")
        for item in grocery.values():
            contributions = item.pop("_contributions", [])
            amount, unit, amount_display = format_summed_amount(contributions)
            amount_details = [
                f"{contribution['amount_text']} ({contribution['source']})"
                for contribution in contributions
                if contribution.get("amount_text")
            ]
            if amount_display:
                item["amount"] = amount
                item["unit"] = unit
                item["amount_display"] = amount_display
                item["amount_details"] = []
            elif amount_details:
                item["amount_display"] = "; ".join(amount_details)
                item["amount_details"] = amount_details
            else:
                item["amount_details"] = []
        grocery_items = sorted(grocery.values(), key=lambda item: (item["category"], item["label"]))
        prep_items = sorted(prep.values(), key=lambda item: item["label"])
        self._apply_checklist_state(plan_id, "grocery", grocery_items)
        self._apply_checklist_state(plan_id, "prep", prep_items)
        return {
            "plan_id": plan_id,
            "grocery_items": grocery_items,
            "prep_items": prep_items,
        }

    def update_checklist_item(self, plan_id: str, payload: Any) -> dict:
        self.plan_response(plan_id)
        label = payload.label.strip()
        if not label:
            raise KeyError(plan_id)
        item_id = checklist_item_id(plan_id, payload.kind, label)
        timestamp = now_iso()
        self.conn.execute(
            """
            INSERT INTO checklist_items(
              id, weekly_plan_id, kind, label, category, source, checked, custom,
              position, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              category = excluded.category,
              source = excluded.source,
              checked = excluded.checked,
              updated_at = excluded.updated_at
            """,
            (
                item_id,
                plan_id,
                payload.kind,
                label,
                payload.category,
                payload.source,
                1 if payload.checked else 0,
                timestamp,
                timestamp,
            ),
        )
        self.conn.commit()
        return self.grocery_prep(plan_id)

    def _apply_checklist_state(self, plan_id: str, kind: str, items: list[dict]) -> None:
        rows = self.conn.execute(
            """
            SELECT *
            FROM checklist_items
            WHERE weekly_plan_id = ? AND kind = ?
            """,
            (plan_id, kind),
        ).fetchall()
        saved = {row["label"].strip().lower(): row for row in rows}
        seen: set[str] = set()
        for item in items:
            key = item["label"].strip().lower()
            seen.add(key)
            item["id"] = checklist_item_id(plan_id, kind, item["label"])
            item["kind"] = kind
            if key in saved:
                item["checked"] = bool(saved[key]["checked"])
        for key, row in saved.items():
            if key in seen or not row["custom"]:
                continue
            items.append(
                {
                    "id": row["id"],
                    "kind": kind,
                    "label": row["label"],
                    "category": row["category"] or "General",
                    "source": row["source"] or "Custom",
                    "checked": bool(row["checked"]),
                }
            )

    def options_by_id(self, option_ids: Any) -> dict[str, dict]:
        ids = list(option_ids)
        if not ids:
            return {}
        placeholders = ",".join("?" for _ in ids)
        rows = self.conn.execute(f"SELECT id FROM variation_options WHERE id IN ({placeholders})", ids)
        return {row["id"]: self.get_option(row["id"]) for row in rows}

    def export_data(self) -> dict:
        return {
            "version": 1,
            "preferences": self.get_preferences(),
            "household": self.household_config(),
            "meals": self.list_meals(include_archived=True),
            "plans": [self.plan_response(row["id"]) for row in self.conn.execute("SELECT id FROM weekly_plans")],
            "events": self.list_events(limit=10000),
            "checklist_items": [row_dict(row) for row in self.conn.execute("SELECT * FROM checklist_items")],
        }

    def import_data(self, data: dict[str, Any], confirm_overwrite: bool = False) -> dict:
        if not confirm_overwrite:
            raise ValueError("Import requires overwrite confirmation.")
        self._validate_export_shape(data)

        from .migrations import init_db

        temp = sqlite3.connect(":memory:")
        temp.row_factory = sqlite3.Row
        temp.execute("PRAGMA foreign_keys = ON")
        try:
            init_db(temp)
            temp_store = Store(temp)
            try:
                temp_store._restore_export_rows(data)
                temp_violations = temp.execute("PRAGMA foreign_key_check").fetchall()
                if temp_violations:
                    raise ValueError("Import data contains invalid linked records.")
            except sqlite3.Error as exc:
                raise ValueError("Import data contains invalid linked records.") from exc

            try:
                with self.conn:
                    self._restore_export_rows(data)
                    violations = self.conn.execute("PRAGMA foreign_key_check").fetchall()
                    if violations:
                        raise ValueError("Import data contains invalid linked records.")
            except sqlite3.Error as exc:
                raise ValueError("Import data contains invalid linked records.") from exc
        finally:
            temp.close()

        counts = {
            "meals": len(data.get("meals", [])),
            "variation_dimensions": sum(len(meal.get("variation_dimensions", [])) for meal in data.get("meals", [])),
            "variation_options": sum(
                len(dimension.get("options", []))
                for meal in data.get("meals", [])
                for dimension in meal.get("variation_dimensions", [])
            ),
            "plans": len(data.get("plans", [])),
            "planned_meals": sum(len(plan.get("planned_meals", [])) for plan in data.get("plans", [])),
            "vacation_blocks": sum(len(plan.get("vacation_blocks", [])) for plan in data.get("plans", [])),
            "events": len(data.get("events", [])),
            "checklist_items": len(data.get("checklist_items", [])),
            "household_members": len(data.get("household", {}).get("members", [])),
            "dietary_profiles": len(data.get("household", {}).get("dietary_profiles", [])),
        }
        return {"imported": counts, "household": self.household_config()}

    def _validate_export_shape(self, data: dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise ValueError("Import file must be a Family Menu JSON object.")
        if data.get("version") != 1:
            raise ValueError("Unsupported Family Menu export version.")
        for key in ["preferences", "household", "meals", "plans", "events", "checklist_items"]:
            if key not in data:
                raise ValueError(f"Import file is missing {key}.")
        if not isinstance(data["household"], dict):
            raise ValueError("Import household data is invalid.")
        for key in ["meals", "plans", "events", "checklist_items"]:
            if not isinstance(data[key], list):
                raise ValueError(f"Import {key} must be a list.")

    def _restore_export_rows(self, data: dict[str, Any]) -> None:
        self._clear_app_rows()
        timestamp = now_iso()
        preferences = Preferences(**data["preferences"]).model_dump()
        self.conn.execute(
            """
            INSERT INTO preferences(id, data, updated_at)
            VALUES (1, ?, ?)
            """,
            (dumps(preferences), timestamp),
        )
        household = data.get("household", {})
        for profile in household.get("dietary_profiles", []):
            self.conn.execute(
                """
                INSERT INTO dietary_profiles(
                  id, name, type, excluded_tags, included_tags, notes, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile["id"],
                    profile["name"],
                    profile.get("type", "custom"),
                    dumps(profile.get("excluded_tags", [])),
                    dumps(profile.get("included_tags", [])),
                    profile.get("notes"),
                    profile.get("created_at") or timestamp,
                    profile.get("updated_at") or timestamp,
                ),
            )
        for member in household.get("members", []):
            self.conn.execute(
                """
                INSERT INTO household_members(
                  id, display_name, status, dinner_servings, leftover_lunch_servings,
                  dietary_profile_ids, preference_tags, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    member["id"],
                    member["display_name"],
                    member.get("status", "active"),
                    member.get("dinner_servings", 1),
                    member.get("leftover_lunch_servings", 0),
                    dumps(member.get("dietary_profile_ids", [])),
                    dumps(member.get("preference_tags", [])),
                    member.get("created_at") or timestamp,
                    member.get("updated_at") or timestamp,
                ),
            )
        for meal in data.get("meals", []):
            self._insert_imported_meal(meal, timestamp)
            for index, dimension in enumerate(meal.get("variation_dimensions", [])):
                self._insert_imported_dimension(meal["id"], dimension, index, timestamp)
                for option in dimension.get("options", []):
                    self._insert_imported_option(meal["id"], dimension["id"], option, timestamp)
        for plan in data.get("plans", []):
            self._insert_imported_plan(plan, timestamp)
            for block in plan.get("vacation_blocks", []):
                self._insert_imported_vacation_block(plan["id"], block, timestamp)
            for planned in plan.get("planned_meals", []):
                self._insert_imported_planned_meal(plan["id"], planned, timestamp)
        for event in data.get("events", []):
            self._insert_imported_event(event, timestamp)
        for item in data.get("checklist_items", []):
            self._insert_imported_checklist_item(item, timestamp)

    def _clear_app_rows(self) -> None:
        for table in [
            "checklist_items",
            "meal_events",
            "planned_meals",
            "vacation_blocks",
            "weekly_plans",
            "variation_options",
            "variation_dimensions",
            "meals",
            "household_members",
            "dietary_profiles",
            "preferences",
        ]:
            self.conn.execute(f"DELETE FROM {table}")

    def _insert_imported_meal(self, meal: dict[str, Any], timestamp: str) -> None:
        self.conn.execute(
            """
            INSERT INTO meals(
              id, name, status, likability, active_prep_minutes, cook_minutes,
              make_ahead_score, leftover_quality, leftover_style, tags,
              diet_tags, shared_ingredients, primary_proteins, alternate_proteins,
              prep_ahead, instructions, source_url, source_name,
              simple_serving_variations, notes, user_modified, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                meal["id"],
                meal["name"],
                meal.get("status", "active"),
                meal.get("likability", 80),
                meal.get("active_prep_minutes", 20),
                meal.get("cook_minutes", 20),
                meal.get("make_ahead_score", 50),
                meal.get("leftover_quality", 70),
                meal.get("leftover_style", "mixed"),
                dumps(meal.get("tags", [])),
                dumps(meal.get("diet_tags", [])),
                dumps(normalize_ingredient_items(meal.get("shared_ingredients", []))),
                dumps(meal.get("primary_proteins", [])),
                dumps(meal.get("alternate_proteins", [])),
                dumps(meal.get("prep_ahead", [])),
                dumps(meal.get("instructions", [])),
                meal.get("source_url"),
                meal.get("source_name"),
                dumps(meal.get("simple_serving_variations", [])),
                meal.get("notes"),
                meal.get("created_at") or timestamp,
                meal.get("updated_at") or timestamp,
            ),
        )

    def _insert_imported_dimension(
        self,
        meal_id: str,
        dimension: dict[str, Any],
        index: int,
        timestamp: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO variation_dimensions(
              id, meal_id, key, name, selection_mode, required, display_order,
              status, color, user_modified, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                dimension["id"],
                meal_id,
                dimension["key"],
                dimension["name"],
                dimension.get("selection_mode", "single"),
                1 if dimension.get("required") else 0,
                dimension.get("display_order", index),
                dimension.get("status", "active"),
                dimension.get("color"),
                dimension.get("created_at") or timestamp,
                dimension.get("updated_at") or timestamp,
            ),
        )

    def _insert_imported_option(
        self,
        meal_id: str,
        dimension_id: str,
        option: dict[str, Any],
        timestamp: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO variation_options(
              id, dimension_id, meal_id, name, status, likability, value,
              diet_tags, compatible_diet_profiles, ingredient_additions,
              ingredient_omissions, prep_ahead, instructions, tags, overrides,
              user_modified, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                option["id"],
                dimension_id,
                meal_id,
                option["name"],
                option.get("status", "active"),
                option.get("likability", 80),
                dumps(option.get("value", {})),
                dumps(option.get("diet_tags", [])),
                dumps(option.get("compatible_diet_profiles", [])),
                dumps(normalize_ingredient_items(option.get("ingredient_additions", []))),
                dumps(option.get("ingredient_omissions", [])),
                dumps(option.get("prep_ahead", [])),
                dumps(option.get("instructions", [])),
                dumps(option.get("tags", [])),
                dumps(option.get("overrides", {})),
                option.get("created_at") or timestamp,
                option.get("updated_at") or timestamp,
            ),
        )

    def _insert_imported_plan(self, plan: dict[str, Any], timestamp: str) -> None:
        self.conn.execute(
            """
            INSERT INTO weekly_plans(
              id, week_start_date, shopping_date, target_dinner_count, status, notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                plan["id"],
                plan["week_start_date"],
                plan["shopping_date"],
                plan.get("target_dinner_count", 5),
                plan.get("status", "draft"),
                plan.get("notes"),
                plan.get("created_at") or timestamp,
                plan.get("updated_at") or timestamp,
            ),
        )

    def _insert_imported_vacation_block(self, plan_id: str, block: dict[str, Any], timestamp: str) -> None:
        self.conn.execute(
            """
            INSERT INTO vacation_blocks(
              id, weekly_plan_id, start_date, end_date, scope, label, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                block["id"],
                plan_id,
                block["start_date"],
                block["end_date"],
                block.get("scope", "day"),
                block.get("label", "Vacation"),
                block.get("created_at") or timestamp,
                block.get("updated_at") or timestamp,
            ),
        )

    def _insert_imported_planned_meal(self, plan_id: str, planned: dict[str, Any], timestamp: str) -> None:
        self.conn.execute(
            """
            INSERT INTO planned_meals(
              id, weekly_plan_id, meal_id, variation_selections, planned_date, position,
              meal_slot, servings_dinner, leftover_lunch_servings, locked, variation_locks,
              state, notes, recommendation_reasons, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                planned["id"],
                plan_id,
                planned["meal_id"],
                dumps(planned.get("variation_selections", {})),
                planned["planned_date"],
                planned.get("position", 0),
                planned.get("meal_slot", "dinner"),
                planned.get("servings_dinner", 4),
                planned.get("leftover_lunch_servings", 2),
                1 if planned.get("locked") else 0,
                dumps(planned.get("variation_locks", {})),
                planned.get("state", "planned"),
                planned.get("notes"),
                dumps(planned.get("recommendation_reasons", [])),
                planned.get("created_at") or timestamp,
                planned.get("updated_at") or timestamp,
            ),
        )

    def _insert_imported_event(self, event: dict[str, Any], timestamp: str) -> None:
        self.conn.execute(
            """
            INSERT INTO meal_events(
              id, meal_id, planned_meal_id, eaten_date, variation_selections,
              servings_dinner, leftover_lunch_servings, feedback, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["id"],
                event["meal_id"],
                event.get("planned_meal_id"),
                event["eaten_date"],
                dumps(event.get("variation_selections", {})),
                event.get("servings_dinner", 4),
                event.get("leftover_lunch_servings", 2),
                event.get("feedback"),
                event.get("notes"),
                event.get("created_at") or timestamp,
            ),
        )

    def _insert_imported_checklist_item(self, item: dict[str, Any], timestamp: str) -> None:
        self.conn.execute(
            """
            INSERT INTO checklist_items(
              id, weekly_plan_id, kind, label, category, source, checked, custom,
              position, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["id"],
                item["weekly_plan_id"],
                item["kind"],
                item["label"],
                item.get("category"),
                item.get("source"),
                1 if item.get("checked") else 0,
                1 if item.get("custom") else 0,
                item.get("position", 0),
                item.get("created_at") or timestamp,
                item.get("updated_at") or timestamp,
            ),
        )


def ingredient_category(label: str) -> str:
    lower = label.lower()
    if any(word in lower for word in ["protein", "tofu", "lentil", "beans", "legume"]):
        return "Protein"
    if any(word in lower for word in ["vegetable", "greens", "produce", "fruit", "herb"]):
        return "Produce"
    if any(word in lower for word in ["base", "starch", "grain", "noodle", "bread"]):
        return "Grains"
    if any(word in lower for word in ["dairy", "cheese", "yogurt"]):
        return "Dairy"
    if any(word in lower for word in ["sauce", "seasoning", "broth"]):
        return "Sauces and Pantry"
    return "General"
