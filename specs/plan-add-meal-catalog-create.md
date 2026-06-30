# Plan: Add Meal Creation to Meal Catalog

## Goal

Allow a user to create a new active meal from the Meal Catalog UI, persist it through the API and SQLite store, and immediately use it like any other catalog meal.

## Implementation Steps

1. Backend schema and API contract
   - Add a `MealCreate` Pydantic model in `family-menu/src/family_menu/schemas.py`.
   - Require a non-empty `name`; keep the rest of the editable meal fields optional with the same defaults as `Meal`.
   - Add `POST /api/v1/meals` in `family-menu/src/family_menu/app.py` with `201 Created`.

2. Backend persistence
   - Add `Store.create_meal(...)` in `family-menu/src/family_menu/store.py`.
   - Reuse the existing `slugify()` helper to derive the meal id from the name.
   - Add a suffix such as `-2`, `-3`, etc. when the slug already exists.
   - Insert active meal defaults, JSON-list fields, timestamps, and `user_modified = 1`.
   - Return the complete `meal_response()` with an empty `variation_dimensions` array.

3. Frontend API support
   - Add `createMeal(payload: Partial<Meal>)` to `family-menu/frontend/src/app/core/api.service.ts`.
   - Keep the TypeScript model shape unchanged unless implementation needs a dedicated create payload type.

4. Meal Catalog UI behavior
   - Add a Create meal button in `family-menu/frontend/src/app/meal-catalog/meal-catalog.component.html`, near the catalog list/search actions.
   - Track draft creation state in `meal-catalog.component.ts`, including the previously selected meal.
   - Start a new editable draft with neutral defaults and no variation dimensions.
   - Reuse the existing form serialization for create and update, routing Save to `createMeal()` while the selected item is a draft.
   - Validate empty/whitespace-only names before sending the request and keep the draft editable with a clear error.
   - On successful create, reload/select the created meal in read-only mode.
   - On cancel, discard the draft and restore the previous selection or no selection.
   - Keep variation add/edit controls hidden or inert until the draft has been saved as a real meal.

5. Tests and verification
   - Add backend tests in `tests/test_catalog.py` for successful create, default values, persisted editable fields, unique id suffixing, empty-name rejection, and replacement-list visibility through `GET /api/v1/meals`.
   - Run `.venv/bin/python -m pytest -q`.
   - Run `npm run build` in `family-menu/frontend`.
   - Start the app locally if practical, verify the Create meal flow in a browser at desktop and phone-sized widths, and confirm the created meal appears in Weekly Plan replacement choices after refresh/navigation.

## Risks and Notes

- Existing weekly plans and history are unaffected because creation only inserts a catalog meal.
- Created meals are private local database data and should not alter tracked starter catalog files.
- The initial frontend flow will not create variation dimensions until after the meal itself is saved, matching the approved spec.
- If manual browser verification is blocked by local environment issues, record the blocker and rely on pytest plus Angular build output.
