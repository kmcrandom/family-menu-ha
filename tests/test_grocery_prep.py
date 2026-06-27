from __future__ import annotations


def test_grocery_prep_includes_option_values(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    response = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep")
    assert response.status_code == 200
    labels = {item["label"] for item in response.json()["grocery_items"]}
    assert labels
    assert any(label in labels for label in {"base ingredient", "default sauce", "compatible protein"})


def test_grocery_prep_checked_state_persists(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    grocery = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep").json()
    item = grocery["grocery_items"][0]

    response = client.patch(
        f"/api/v1/plans/{generated['id']}/checklist-items",
        json={**item, "kind": "grocery", "checked": True},
    )

    assert response.status_code == 200
    reloaded = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep").json()
    checked_item = next(candidate for candidate in reloaded["grocery_items"] if candidate["label"] == item["label"])
    assert checked_item["checked"] is True


def test_catalog_grocery_and_prep_edits_feed_generated_lists(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    planned = next(item for item in generated["planned_meals"] if item["variation_selections"])
    option_id = next(iter(planned["variation_selections"].values()))

    meal_patch = client.patch(
        f"/api/v1/meals/{planned['meal_id']}",
        json={
            "shared_ingredients": ["catalog meal ingredient"],
            "prep_ahead": ["catalog meal prep task"],
        },
    )
    option_patch = client.patch(
        f"/api/v1/variation-options/{option_id}",
        json={
            "ingredient_additions": ["catalog option ingredient"],
            "prep_ahead": ["catalog option prep task"],
        },
    )

    assert meal_patch.status_code == 200
    assert option_patch.status_code == 200
    grocery = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep").json()

    grocery_labels = {item["label"] for item in grocery["grocery_items"]}
    prep_labels = {item["label"] for item in grocery["prep_items"]}
    assert "catalog meal ingredient" in grocery_labels
    assert "catalog option ingredient" in grocery_labels
    assert "catalog meal prep task" in prep_labels
    assert "catalog option prep task" in prep_labels


def test_option_omissions_remove_matching_shared_ingredients(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    planned = next(item for item in generated["planned_meals"] if item["variation_selections"])
    option_id = next(iter(planned["variation_selections"].values()))

    client.patch(
        f"/api/v1/meals/{planned['meal_id']}",
        json={"shared_ingredients": ["Base Ingredient", "keep ingredient"]},
    )
    client.patch(
        f"/api/v1/variation-options/{option_id}",
        json={"ingredient_omissions": [" base ingredient "]},
    )

    grocery = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep").json()
    labels = {item["label"] for item in grocery["grocery_items"]}
    assert "Base Ingredient" not in labels
    assert "keep ingredient" in labels


def test_option_omission_does_not_remove_other_sources(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    planned_with_option = next(item for item in generated["planned_meals"] if item["variation_selections"])
    other_planned = next(item for item in generated["planned_meals"] if item["id"] != planned_with_option["id"])
    option_id = next(iter(planned_with_option["variation_selections"].values()))

    client.patch(
        f"/api/v1/meals/{planned_with_option['meal_id']}",
        json={"shared_ingredients": ["shared item"]},
    )
    client.patch(
        f"/api/v1/meals/{other_planned['meal_id']}",
        json={"shared_ingredients": ["shared item"]},
    )
    client.patch(
        f"/api/v1/variation-options/{option_id}",
        json={
            "ingredient_additions": ["shared item"],
            "ingredient_omissions": ["shared item"],
        },
    )

    grocery = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep").json()
    matching_items = [item for item in grocery["grocery_items"] if item["label"] == "shared item"]
    assert len(matching_items) == 1
    assert other_planned["meal"]["name"] in matching_items[0]["source"]
    assert planned_with_option["meal"]["name"] in matching_items[0]["source"]


def test_legacy_string_ingredients_are_normalized(client):
    meal = client.get("/api/v1/meals").json()[0]
    response = client.patch(
        f"/api/v1/meals/{meal['id']}",
        json={"shared_ingredients": ["legacy ingredient"]},
    )

    assert response.status_code == 200
    assert response.json()["shared_ingredients"] == [{"label": "legacy ingredient"}]


def test_grocery_sums_weight_units(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    planned = next(item for item in generated["planned_meals"] if item["variation_selections"])
    option_id = next(iter(planned["variation_selections"].values()))

    client.patch(
        f"/api/v1/meals/{planned['meal_id']}",
        json={"shared_ingredients": [{"label": "flour", "amount": "1", "unit": "lb"}]},
    )
    client.patch(
        f"/api/v1/variation-options/{option_id}",
        json={"ingredient_additions": [{"label": "flour", "amount": "8", "unit": "oz"}]},
    )

    grocery = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep").json()
    flour = next(item for item in grocery["grocery_items"] if item["label"] == "flour")
    assert flour["amount_display"] == "1.5 lb"


def test_grocery_sums_volume_units_and_fractions(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    planned = next(item for item in generated["planned_meals"] if item["variation_selections"])
    option_id = next(iter(planned["variation_selections"].values()))

    client.patch(
        f"/api/v1/meals/{planned['meal_id']}",
        json={"shared_ingredients": [{"label": "stock", "amount": "1/2", "unit": "cup"}]},
    )
    client.patch(
        f"/api/v1/variation-options/{option_id}",
        json={"ingredient_additions": [{"label": "stock", "amount": "8", "unit": "tbsp"}]},
    )

    grocery = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep").json()
    stock = next(item for item in grocery["grocery_items"] if item["label"] == "stock")
    assert stock["amount_display"] == "1 cups"


def test_grocery_sums_simple_count_amounts(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    planned = next(item for item in generated["planned_meals"] if item["variation_selections"])
    option_id = next(iter(planned["variation_selections"].values()))

    client.patch(
        f"/api/v1/meals/{planned['meal_id']}",
        json={"shared_ingredients": [{"label": "carrots", "amount": "5"}]},
    )
    client.patch(
        f"/api/v1/variation-options/{option_id}",
        json={"ingredient_additions": [{"label": "carrots", "amount": "2"}]},
    )

    grocery = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep").json()
    carrots = next(item for item in grocery["grocery_items"] if item["label"] == "carrots")
    assert carrots["amount_display"] == "7"


def test_grocery_preserves_incompatible_amount_details(client):
    plan = client.get("/api/v1/plans/current").json()
    generated = client.post(f"/api/v1/plans/{plan['id']}/generate", json={}).json()
    planned = next(item for item in generated["planned_meals"] if item["variation_selections"])
    option_id = next(iter(planned["variation_selections"].values()))

    client.patch(
        f"/api/v1/meals/{planned['meal_id']}",
        json={"shared_ingredients": [{"label": "salt", "amount": "to taste"}]},
    )
    client.patch(
        f"/api/v1/variation-options/{option_id}",
        json={"ingredient_additions": [{"label": "salt", "amount": "1", "unit": "tsp"}]},
    )

    grocery = client.get(f"/api/v1/plans/{generated['id']}/grocery-prep").json()
    salt = next(item for item in grocery["grocery_items"] if item["label"] == "salt")
    assert "to taste" in salt["amount_display"]
    assert "1 tsp" in salt["amount_display"]
    assert len(salt["amount_details"]) == 2
