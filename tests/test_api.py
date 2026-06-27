from __future__ import annotations


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_current_plan_generates_five_distinct_meals(client):
    plan = client.get("/api/v1/plans/current").json()
    response = client.post(f"/api/v1/plans/{plan['id']}/generate", json={})
    assert response.status_code == 200
    generated = response.json()
    planned = generated["planned_meals"]
    assert len(planned) == 5
    assert len({item["meal_id"] for item in planned}) == 5
    assert all(item["variation_selections"] for item in planned)


def test_replace_meal_resets_variation_selections(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    first = generated["planned_meals"][0]
    meal = next(meal for meal in client.get("/api/v1/meals").json() if meal["id"] != first["meal_id"])
    response = client.patch(f"/api/v1/planned-meals/{first['id']}", json={"meal_id": meal["id"]})
    assert response.status_code == 200
    updated = response.json()
    assert updated["meal_id"] == meal["id"]
    assert set(updated["variation_selections"]) == {
        dimension["id"] for dimension in meal["variation_dimensions"]
    }


def test_household_config_can_edit_members_and_profiles(client):
    household = client.get("/api/v1/household").json()
    assert household["members"]
    assert household["dietary_profiles"]
    created_profile = client.post(
        "/api/v1/household/dietary-profiles",
        json={"name": "No Sample Tag", "type": "custom", "excluded_tags": ["sample_excluded"]},
    )
    assert created_profile.status_code == 201
    profile = created_profile.json()
    created_member = client.post(
        "/api/v1/household/members",
        json={
            "display_name": "Eater 2",
            "dinner_servings": 1,
            "leftover_lunch_servings": 0.5,
            "dietary_profile_ids": [profile["id"]],
        },
    )
    assert created_member.status_code == 201
    member = created_member.json()
    patched = client.patch(
        f"/api/v1/household/members/{member['id']}",
        json={"dinner_servings": 1.5},
    )
    assert patched.status_code == 200
    assert patched.json()["dinner_servings"] == 1.5
    mode = client.patch("/api/v1/preferences", json={"mixed_diet_mode": "common_compatible_only"})
    assert mode.status_code == 200
    assert mode.json()["mixed_diet_mode"] == "common_compatible_only"
