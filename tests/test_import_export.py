from __future__ import annotations


def test_import_restores_exported_app_data(client):
    household = client.get("/api/v1/household").json()
    profile = client.post(
        "/api/v1/household/dietary-profiles",
        json={"name": "Restore Profile", "type": "custom", "excluded_tags": ["restore_tag"]},
    ).json()
    member = client.post(
        "/api/v1/household/members",
        json={
            "display_name": "Restore Eater",
            "dinner_servings": 1.5,
            "leftover_lunch_servings": 0.5,
            "dietary_profile_ids": [profile["id"]],
        },
    ).json()
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    vacation = client.post(
        f"/api/v1/plans/{generated['id']}/vacation-blocks",
        json={"start_date": generated["week_start_date"], "scope": "day", "label": "Away"},
    )
    assert vacation.status_code == 201
    generated = vacation.json()
    planned = generated["planned_meals"][0]
    event = client.post(f"/api/v1/planned-meals/{planned['id']}/mark-eaten").json()
    grocery = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep").json()
    item = grocery["grocery_items"][0]
    checklist = client.patch(
        f"/api/v1/plans/{generated['id']}/checklist-items",
        json={**item, "kind": "grocery", "checked": True},
    )
    assert checklist.status_code == 200

    exported = client.get("/api/v1/export").json()
    exported_meal_count = len(exported["meals"])

    first_meal = exported["meals"][0]
    client.patch(f"/api/v1/meals/{first_meal['id']}", json={"name": "Changed after export"})
    client.patch("/api/v1/preferences", json={"household_name": "Changed Household"})
    client.delete(f"/api/v1/history/{event['id']}")

    response = client.post("/api/v1/import", json={"data": exported, "confirm_overwrite": True})

    assert response.status_code == 200
    imported = response.json()["imported"]
    assert imported["meals"] == exported_meal_count
    assert imported["plans"] == len(exported["plans"])
    assert imported["events"] == len(exported["events"])
    assert imported["checklist_items"] == len(exported["checklist_items"])
    restored_household = client.get("/api/v1/household").json()
    assert restored_household["preferences"]["household_name"] == household["preferences"]["household_name"]
    assert any(candidate["id"] == member["id"] for candidate in restored_household["members"])
    assert client.get(f"/api/v1/meals/{first_meal['id']}").json()["name"] == first_meal["name"]
    assert client.get("/api/v1/history").json()[0]["id"] == event["id"]


def test_import_requires_overwrite_confirmation(client):
    exported = client.get("/api/v1/export").json()
    original_count = len(client.get("/api/v1/meals").json())

    response = client.post("/api/v1/import", json={"data": exported, "confirm_overwrite": False})

    assert response.status_code == 400
    assert len(client.get("/api/v1/meals").json()) == original_count


def test_import_rejects_invalid_shape_without_changing_data(client):
    original_meal = client.get("/api/v1/meals").json()[0]

    response = client.post("/api/v1/import", json={"data": {"version": 99}, "confirm_overwrite": True})

    assert response.status_code == 400
    assert client.get(f"/api/v1/meals/{original_meal['id']}").json()["name"] == original_meal["name"]


def test_import_rolls_back_invalid_linked_data(client):
    exported = client.get("/api/v1/export").json()
    original_meal = client.get("/api/v1/meals").json()[0]
    exported["events"].append(
        {
            "id": "event-broken",
            "meal_id": "missing-meal",
            "planned_meal_id": None,
            "eaten_date": "2026-06-27",
            "variation_selections": {},
            "servings_dinner": 1,
            "leftover_lunch_servings": 0,
            "feedback": None,
            "notes": None,
            "created_at": "2026-06-27T12:00:00",
        }
    )

    response = client.post("/api/v1/import", json={"data": exported, "confirm_overwrite": True})

    assert response.status_code == 400
    assert client.get(f"/api/v1/meals/{original_meal['id']}").json()["name"] == original_meal["name"]
