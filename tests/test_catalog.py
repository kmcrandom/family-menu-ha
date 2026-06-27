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
