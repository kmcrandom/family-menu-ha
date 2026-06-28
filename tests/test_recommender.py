from __future__ import annotations

from datetime import date

from family_menu import recommender


def test_ranked_candidate_choice_uses_bounded_random_window(monkeypatch):
    choices_seen = []

    def choose_last(candidates):
        choices_seen.append(candidates)
        return candidates[-1]

    monkeypatch.setattr(recommender.random, "choice", choose_last)

    selected = recommender.choose_ranked_candidate(
        [
            (70, "low", {"id": "low"}),
            (94, "second", {"id": "second"}),
            (100, "best", {"id": "best"}),
            (84, "outside-window", {"id": "outside-window"}),
        ]
    )

    assert [candidate[1] for candidate in choices_seen[0]] == ["best", "second"]
    assert selected[2]["id"] == "second"


def test_regeneration_can_change_unlocked_meals_with_controlled_randomness(client, monkeypatch):
    plan = client.get("/api/v1/plans/current").json()
    monkeypatch.setattr(recommender.random, "choice", lambda candidates: candidates[0])
    first = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()

    monkeypatch.setattr(recommender.random, "choice", lambda candidates: candidates[-1])
    second = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()

    first_meals = [item["meal_id"] for item in first["planned_meals"]]
    second_meals = [item["meal_id"] for item in second["planned_meals"]]
    assert first_meals != second_meals
    assert len(set(second_meals)) == len(second_meals)


def test_locked_meal_survives_regeneration(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    locked = generated["planned_meals"][1]
    client.patch(f"/api/v1/planned-meals/{locked['id']}", json={"locked": True})
    regenerated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    match = next(item for item in regenerated["planned_meals"] if item["position"] == locked["position"])
    assert match["id"] == locked["id"]
    assert match["meal_id"] == locked["meal_id"]


def test_locked_variation_survives_regeneration(monkeypatch):
    def fail_random_choice(candidates):
        raise AssertionError("locked variation should not be randomized")

    monkeypatch.setattr(recommender.random, "choice", fail_random_choice)

    selections, reasons = recommender.choose_variation_options(
        {
            "variation_dimensions": [
                {
                    "id": "meal-protein",
                    "options": [
                        {"id": "chicken", "name": "Chicken", "status": "active", "likability": 90},
                        {"id": "tofu", "name": "Tofu", "status": "active", "likability": 80},
                    ],
                }
            ]
        },
        {"option_counts": {}, "last_option": {}},
        date(2026, 7, 1),
        {
            "variation_selections": {"meal-protein": "tofu"},
            "variation_locks": {"meal-protein": True},
        },
        regenerate_variations=True,
    )

    assert selections == {"meal-protein": "tofu"}
    assert reasons == ["variation_locked_by_user"]


def test_history_changes_option_suggestions(client, monkeypatch):
    monkeypatch.setattr(recommender.random, "choice", lambda candidates: candidates[0])
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    meal_with_choices = next(
        item
        for item in generated["planned_meals"]
        if any(
            len(dimension["options"]) > 1
            for dimension in item["meal"]["variation_dimensions"]
        )
    )
    primary_dimension = next(
        dimension
        for dimension in meal_with_choices["meal"]["variation_dimensions"]
        if len(dimension["options"]) > 1
    )
    original_option = meal_with_choices["variation_selections"][primary_dimension["id"]]
    for _ in range(4):
        client.post(f"/api/v1/planned-meals/{meal_with_choices['id']}/mark-eaten")
    new_plan = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    new_match = next((item for item in new_plan["planned_meals"] if item["meal_id"] == meal_with_choices["meal_id"]), None)
    if new_match is not None:
        assert new_match["variation_selections"][primary_dimension["id"]] != original_option


def test_common_compatible_mode_filters_incompatible_meals(client):
    household = client.get("/api/v1/household").json()
    profile = client.post(
        "/api/v1/household/dietary-profiles",
        json={"name": "Plant Forward", "type": "vegetarian"},
    ).json()
    member = household["members"][0]
    client.patch(
        f"/api/v1/household/members/{member['id']}",
        json={"dietary_profile_ids": [profile["id"]]},
    )
    client.patch("/api/v1/preferences", json={"mixed_diet_mode": "common_compatible_only"})
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    assert all(item["meal_id"] != "sample-sheet-pan-dinner" for item in generated["planned_meals"])


def test_separate_variations_allow_distinct_diet_protein_dimensions(client):
    household = client.get("/api/v1/household").json()
    profile = client.post(
        "/api/v1/household/dietary-profiles",
        json={
            "name": "Pescatarian",
            "type": "pescatarian",
            "excluded_tags": ["contains_meat"],
        },
    ).json()
    member = household["members"][0]
    client.patch(
        f"/api/v1/household/members/{member['id']}",
        json={"dietary_profile_ids": [profile["id"]]},
    )
    client.patch("/api/v1/preferences", json={"mixed_diet_mode": "separate_variations"})

    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()

    assert len(generated["planned_meals"]) == 5
    assert any(item["meal_id"] == "sample-sheet-pan-dinner" for item in generated["planned_meals"])


def test_full_week_vacation_removes_existing_meals_and_blocks_generation(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    assert len(generated["planned_meals"]) == 5

    vacation = client.post(
        f"/api/v1/plans/{plan['id']}/vacation-blocks",
        json={"start_date": plan["week_start_date"], "scope": "week"},
    )
    assert vacation.status_code == 201
    blocked = vacation.json()
    assert len(blocked["vacation_blocks"]) == 1
    assert blocked["planned_meals"] == []

    regenerated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    assert regenerated["planned_meals"] == []


def test_day_vacation_removes_that_day_and_generation_skips_date(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    vacation_meal = generated["planned_meals"][2]
    vacation_date = vacation_meal["planned_date"]
    client.patch(f"/api/v1/planned-meals/{vacation_meal['id']}", json={"locked": True})

    blocked = client.post(
        f"/api/v1/plans/{plan['id']}/vacation-blocks",
        json={"start_date": vacation_date, "scope": "day"},
    ).json()
    assert all(item["planned_date"] != vacation_date for item in blocked["planned_meals"])

    regenerated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    assert len(regenerated["planned_meals"]) == 4
    assert all(item["planned_date"] != vacation_date for item in regenerated["planned_meals"])


def test_deleting_vacation_block_does_not_auto_generate_meals(client):
    plan = client.get("/api/v1/plans/current").json()
    client.post(f"/api/v1/plans/{plan['id']}/generate", json={})
    blocked = client.post(
        f"/api/v1/plans/{plan['id']}/vacation-blocks",
        json={"start_date": plan["week_start_date"], "scope": "week"},
    ).json()

    restored = client.delete(f"/api/v1/vacation-blocks/{blocked['vacation_blocks'][0]['id']}").json()
    assert restored["vacation_blocks"] == []
    assert restored["planned_meals"] == []
