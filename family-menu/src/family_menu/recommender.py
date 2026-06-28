from __future__ import annotations

import random
from datetime import date, timedelta
from math import inf
from typing import Any, TypeVar

from .store import Store

ScoredCandidate = TypeVar("ScoredCandidate", bound=tuple)
RANDOM_CANDIDATE_LIMIT = 3
RANDOM_SCORE_WINDOW = 12


def generate_plan(
    store: Store,
    plan_id: str,
    preserve_locked: bool = True,
    regenerate_variations: bool = True,
) -> dict:
    plan = store.plan_response(plan_id)
    prefs = store.get_preferences()
    household = store.household_config()
    profiles = active_dietary_profiles(household)
    mixed_diet_mode = prefs.get("mixed_diet_mode", "separate_variations")
    stats = store.meal_history_stats()
    target_count = plan["target_dinner_count"]
    week_start = date.fromisoformat(plan["week_start_date"])
    blocked_dates = store.vacation_blocked_dates(plan_id)
    existing = plan["planned_meals"]
    locked_positions = {
        item["position"]: item
        for item in existing
        if preserve_locked and item.get("locked") and date.fromisoformat(item["planned_date"]) not in blocked_dates
    }
    used_meals = {item["meal_id"] for item in locked_positions.values()}
    active_meals = [
        meal
        for meal in store.list_meals(include_archived=False)
        if meal_eligible_for_household(meal, profiles, mixed_diet_mode)
    ]
    selections: list[dict[str, Any]] = []
    previous_leftover_style: str | None = None

    for position in range(target_count):
        planned_date = week_start + timedelta(days=position + 1)
        if planned_date in blocked_dates:
            continue
        if position in locked_positions:
            locked = locked_positions[position]
            previous_leftover_style = locked["meal"]["leftover_style"]
            selections.append(
                {
                    "position": position,
                    "planned_date": planned_date,
                    "meal_id": locked["meal_id"],
                    "variation_selections": locked["variation_selections"],
                    "reasons": ["locked_by_user"],
                }
            )
            continue

        meal_scores = []
        for meal in active_meals:
            if meal["id"] in used_meals:
                continue
            score, reasons = score_meal(
                meal,
                stats,
                prefs,
                planned_date,
                previous_leftover_style,
            )
            meal_scores.append((score, meal["name"], meal, reasons))
        if not meal_scores:
            break
        _, _, selected_meal, reasons = choose_ranked_candidate(meal_scores)
        variation_selections, option_reasons = choose_variation_options(
            selected_meal,
            stats,
            planned_date,
            existing_for_position(existing, position),
            regenerate_variations,
            profiles,
            mixed_diet_mode,
        )
        selections.append(
            {
                "position": position,
                "planned_date": planned_date,
                "meal_id": selected_meal["id"],
                "variation_selections": variation_selections,
                "reasons": reasons + option_reasons,
            }
        )
        used_meals.add(selected_meal["id"])
        previous_leftover_style = selected_meal["leftover_style"]

    return store.replace_plan_unlocked(plan_id, selections, blocked_dates=blocked_dates)


def score_meal(
    meal: dict,
    stats: dict,
    prefs: dict,
    planned_date: date,
    previous_leftover_style: str | None,
) -> tuple[float, list[str]]:
    reasons: list[str] = []
    meal_counts = stats["meal_counts"]
    last_meal = stats["last_meal"]
    count = meal_counts.get(meal["id"], 0)
    days_since = None
    if meal["id"] in last_meal:
        days_since = (planned_date - last_meal[meal["id"]]).days

    recency_score = 100 if days_since is None else min(100, max(0, days_since * 5))
    frequency_score = max(0, 100 - count * 18)
    prep_score = (meal["make_ahead_score"] * 0.65) + max(0, 100 - meal["active_prep_minutes"] * 2) * 0.35
    leftover_score = meal["leftover_quality"]
    score = (
        meal["likability"] * prefs["recommendation_weights"].get("likability", 0.34)
        + frequency_score * prefs["recommendation_weights"].get("frequency", 0.24)
        + recency_score * prefs["recommendation_weights"].get("recency", 0.20)
        + prep_score * prefs["recommendation_weights"].get("prep", 0.12)
        + leftover_score * prefs["recommendation_weights"].get("leftovers", 0.10)
    )

    if previous_leftover_style and previous_leftover_style == meal["leftover_style"]:
        score -= 18
    if meal["likability"] >= 85:
        reasons.append("high_likability")
    if count == 0:
        reasons.append("underused")
    if days_since is None or days_since >= prefs.get("soft_repeat_gap_days", 14):
        reasons.append("not_recently_eaten")
    if meal["leftover_quality"] >= 82:
        reasons.append("good_leftovers")
    if meal["make_ahead_score"] >= 80:
        reasons.append("prep_ahead_friendly")
    if previous_leftover_style and previous_leftover_style != meal["leftover_style"]:
        reasons.append("leftover_variety")
    return score, reasons or ["balanced_pick"]


def choose_variation_options(
    meal: dict,
    stats: dict,
    planned_date: date,
    existing: dict | None,
    regenerate_variations: bool,
    profiles: list[dict] | None = None,
    mixed_diet_mode: str = "separate_variations",
) -> tuple[dict[str, str], list[str]]:
    selections: dict[str, str] = {}
    reasons: list[str] = []
    existing_selections = (existing or {}).get("variation_selections", {})
    variation_locks = (existing or {}).get("variation_locks", {})
    for dimension in meal["variation_dimensions"]:
        options = [option for option in dimension["options"] if option["status"] == "active"]
        if mixed_diet_mode == "common_compatible_only":
            options = [option for option in options if option_compatible_with_all_profiles(option, profiles or [])]
        if not options:
            continue
        locked = variation_locks.get(dimension["id"])
        existing_option = existing_selections.get(dimension["id"])
        if existing_option and (locked or not regenerate_variations):
            selections[dimension["id"]] = existing_option
            reasons.append("variation_locked_by_user" if locked else "variation_preserved")
            continue
        scored = [
            (
                score_option(option, stats, planned_date),
                option["name"],
                option,
            )
            for option in options
        ]
        _, _, selected = choose_ranked_candidate(scored)
        selections[dimension["id"]] = selected["id"]
        if selected["likability"] >= 85:
            reasons.append("variation_option_high_likability")
        if stats["option_counts"].get(selected["id"], 0) == 0:
            reasons.append("underused_variation_option")
        elif selected["id"] not in stats["last_option"]:
            reasons.append("not_recently_used_variation_option")
    return selections, sorted(set(reasons))


def score_option(option: dict, stats: dict, planned_date: date) -> float:
    count = stats["option_counts"].get(option["id"], 0)
    last_used = stats["last_option"].get(option["id"])
    days_since = inf if last_used is None else (planned_date - last_used).days
    recency_score = 100 if days_since is inf else min(100, max(0, days_since * 6))
    frequency_score = max(0, 100 - count * 22)
    return option["likability"] * 0.42 + frequency_score * 0.30 + recency_score * 0.28


def choose_ranked_candidate(candidates: list[ScoredCandidate]) -> ScoredCandidate:
    ranked = sorted(candidates, key=lambda item: (-item[0], item[1]))
    window = top_candidate_window(ranked)
    return random.choice(window)


def top_candidate_window(ranked_candidates: list[ScoredCandidate]) -> list[ScoredCandidate]:
    if not ranked_candidates:
        return []
    best_score = ranked_candidates[0][0]
    return [
        candidate
        for index, candidate in enumerate(ranked_candidates)
        if index < RANDOM_CANDIDATE_LIMIT
        and candidate[0] >= best_score - RANDOM_SCORE_WINDOW
    ]


def existing_for_position(existing: list[dict], position: int) -> dict | None:
    return next((item for item in existing if item["position"] == position), None)


def active_dietary_profiles(household: dict) -> list[dict]:
    profiles_by_id = {profile["id"]: profile for profile in household.get("dietary_profiles", [])}
    active_ids: set[str] = set()
    for member in household.get("members", []):
        if member.get("status") != "active":
            continue
        active_ids.update(member.get("dietary_profile_ids", []))
    return [profiles_by_id[profile_id] for profile_id in sorted(active_ids) if profile_id in profiles_by_id]


def meal_eligible_for_household(meal: dict, profiles: list[dict], mixed_diet_mode: str) -> bool:
    if not profiles:
        return True
    if mixed_diet_mode == "common_compatible_only":
        if not tags_compatible_with_all_profiles(meal.get("diet_tags", []), profiles):
            return False
        for dimension in meal.get("variation_dimensions", []):
            if not dimension.get("required"):
                continue
            options = [option for option in dimension.get("options", []) if option.get("status") == "active"]
            if options and not any(option_compatible_with_all_profiles(option, profiles) for option in options):
                return False
        return True
    sensitive_dimensions = [
        dimension
        for dimension in meal.get("variation_dimensions", [])
        if dimension.get("required") and dimension_is_diet_sensitive(dimension)
    ]
    if any(not active_dimension_options(dimension) for dimension in sensitive_dimensions):
        return False
    for profile in profiles:
        if sensitive_dimensions and not any(
            any(option_compatible_with_profile(option, profile) for option in active_dimension_options(dimension))
            for dimension in sensitive_dimensions
        ):
            return False
    return True


def dimension_is_diet_sensitive(dimension: dict) -> bool:
    key = dimension.get("key", "")
    if "protein" in key:
        return True
    return any(
        option.get("diet_tags") or option.get("compatible_diet_profiles")
        for option in dimension.get("options", [])
    )


def active_dimension_options(dimension: dict) -> list[dict]:
    return [option for option in dimension.get("options", []) if option.get("status") == "active"]


def option_compatible_with_all_profiles(option: dict, profiles: list[dict]) -> bool:
    return all(option_compatible_with_profile(option, profile) for profile in profiles)


def option_compatible_with_profile(option: dict, profile: dict) -> bool:
    compatible_ids = option.get("compatible_diet_profiles", [])
    if compatible_ids and profile.get("id") in compatible_ids:
        return True
    return tags_compatible_with_profile(option.get("diet_tags", []), profile)


def tags_compatible_with_all_profiles(tags: list[str], profiles: list[dict]) -> bool:
    return all(tags_compatible_with_profile(tags, profile) for profile in profiles)


def tags_compatible_with_profile(tags: list[str], profile: dict) -> bool:
    if not tags:
        return True
    normalized = {tag.lower() for tag in tags}
    excluded = profile_excluded_tags(profile)
    return normalized.isdisjoint(excluded)


def profile_excluded_tags(profile: dict) -> set[str]:
    profile_type = profile.get("type", "custom")
    excluded = {tag.lower() for tag in profile.get("excluded_tags", [])}
    defaults = {
        "vegetarian": {"contains_meat", "contains_pork", "contains_beef", "contains_poultry"},
        "vegan": {
            "contains_meat",
            "contains_pork",
            "contains_beef",
            "contains_poultry",
            "contains_fish",
            "contains_shellfish",
            "contains_dairy",
            "contains_egg",
        },
        "pescatarian": {"contains_meat", "contains_pork", "contains_beef", "contains_poultry"},
        "no_pork": {"contains_pork"},
        "no_beef": {"contains_beef"},
    }
    return excluded | defaults.get(profile_type, set())
