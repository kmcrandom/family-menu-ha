from __future__ import annotations


def test_patch_meal_likability(client):
    response = client.patch("/api/v1/meals/sample-build-your-own-bowl", json={"likability": 77})
    assert response.status_code == 200
    assert response.json()["likability"] == 77


def test_patch_meal_source_and_instructions(client):
    response = client.patch(
        "/api/v1/meals/sample-build-your-own-bowl",
        json={
            "source_url": "https://example.com/recipe",
            "source_name": "Example Recipe",
            "instructions": ["Prepare ingredients.", "Cook until done."],
        },
    )
    assert response.status_code == 200
    assert response.json()["source_url"] == "https://example.com/recipe"
    assert response.json()["source_name"] == "Example Recipe"
    assert response.json()["instructions"] == ["Prepare ingredients.", "Cook until done."]

    reloaded = client.get("/api/v1/meals/sample-build-your-own-bowl")
    assert reloaded.status_code == 200
    assert reloaded.json()["source_url"] == "https://example.com/recipe"
    assert reloaded.json()["source_name"] == "Example Recipe"
    assert reloaded.json()["instructions"] == ["Prepare ingredients.", "Cook until done."]


def test_add_and_archive_variation_option(client):
    meal = client.get("/api/v1/meals/sample-build-your-own-bowl").json()
    sauce_dimension = next(
        dimension for dimension in meal["variation_dimensions"] if dimension["key"] == "variation_sauce"
    )
    created = client.post(
        f"/api/v1/variation-dimensions/{sauce_dimension['id']}/options",
        json={"name": "sample sauce", "likability": 70, "value": {"sauce": "sample sauce"}},
    )
    assert created.status_code == 201
    option_id = created.json()["id"]
    archived = client.post(f"/api/v1/variation-options/{option_id}/archive")
    assert archived.status_code == 200
    assert archived.json()["status"] == "archived"


def test_add_patch_and_archive_variation_dimension_with_color(client):
    created = client.post(
        "/api/v1/meals/sample-build-your-own-bowl/variation-dimensions",
        json={
            "key": "variation_toppings",
            "name": "Toppings",
            "required": False,
            "display_order": 99,
            "color": "#8bc34a",
        },
    )
    assert created.status_code == 201
    dimension = created.json()
    assert dimension["color"] == "#8bc34a"

    patched = client.patch(
        f"/api/v1/variation-dimensions/{dimension['id']}",
        json={"color": "#ff9800", "required": True},
    )
    assert patched.status_code == 200
    assert patched.json()["color"] == "#ff9800"
    assert patched.json()["required"] is True

    archived = client.post(f"/api/v1/variation-dimensions/{dimension['id']}/archive")
    assert archived.status_code == 200
    assert archived.json()["status"] == "archived"

    active_meal = client.get("/api/v1/meals").json()
    bowl = next(meal for meal in active_meal if meal["id"] == "sample-build-your-own-bowl")
    assert all(candidate["id"] != dimension["id"] for candidate in bowl["variation_dimensions"])

    full_meal = client.get("/api/v1/meals/sample-build-your-own-bowl").json()
    archived_dimension = next(candidate for candidate in full_meal["variation_dimensions"] if candidate["id"] == dimension["id"])
    assert archived_dimension["status"] == "archived"
    assert archived_dimension["color"] == "#ff9800"
