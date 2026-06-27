from __future__ import annotations


def test_seed_imports_meals_dimensions_and_options(client):
    meals = client.get("/api/v1/meals").json()
    dimensions = sum(len(meal["variation_dimensions"]) for meal in meals)
    options = sum(
        len(dimension["options"])
        for meal in meals
        for dimension in meal["variation_dimensions"]
    )
    assert len(meals) == 5
    assert dimensions >= 7
    assert options >= 9


def test_seed_exposes_independent_generic_dimensions(client):
    meal = client.get("/api/v1/meals/sample-build-your-own-bowl").json()
    dimensions = {dimension["key"]: dimension for dimension in meal["variation_dimensions"]}
    assert {option["name"] for option in dimensions["variation_sauce"]["options"]} == {
        "default sauce",
    }
    assert "alternate_proteins" in meal
    assert "simple_serving_variations" in meal
