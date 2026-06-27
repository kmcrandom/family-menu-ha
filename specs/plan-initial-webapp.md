# Initial Web App Implementation Plan

## Scope

Build the first usable local Family Menu web app described by the approved specs:

- FastAPI backend.
- SQLite persistence.
- Angular SPA frontend built to static assets and served by the backend.
- Editable meal catalog with variation dimensions and options.
- Weekly five-dinner plan generation.
- Manual meal replacement, reordering, locking, variation-option swapping, mark eaten, and skip.
- Eating history that influences meal and variation-option recommendations.
- Grocery/prep, history, and settings screens.
- Local export/import.

Home Assistant add-on packaging is prepared for by structure and config, but is not required for the first usable app.

## Non-Scope For This Plan

- Native iOS app.
- Cloud hosting.
- Authentication beyond local development assumptions.
- Exact grocery quantities.
- Pantry inventory.
- Nutrition, macros, and allergens.
- Home Assistant add-on packaging, unless promoted by a later approved plan.

## Proposed Repository Layout

```text
family_menu/
  src/family_menu/
    __init__.py
    __main__.py
    app.py
    config.py
    db.py
    migrations.py
    recommender.py
    schemas.py
    seed.py
    store.py
    static/
      .gitkeep
  data/
    generic-starter-meal-catalog.example.json
  frontend/
    angular.json
    package.json
    package-lock.json
    tsconfig.json
    tsconfig.app.json
    tsconfig.spec.json
    src/
      index.html
      main.ts
      styles.css
      app/
        app.component.ts
        app.routes.ts
        core/
          api.service.ts
          models.ts
        weekly-plan/
        meal-catalog/
        grocery-prep/
        history/
        settings/
  tests/
    test_api.py
    test_catalog.py
    test_grocery_prep.py
    test_history.py
    test_recommender.py
    test_seed.py
  specs/
    ...
pyproject.toml
README.md
AGENTS.md
```

The backend can use the same general shape as MinuteMetrics HA: `pyproject.toml`, FastAPI app factory, SQLite store, static files, and pytest tests. The frontend should be an Angular app using standalone components, typed TypeScript models, Angular services for API access, and reactive forms for catalog/settings editing. FastAPI should serve the Angular production build for local use and future Home Assistant packaging.

## Phase 1: Backend Foundation

Files likely changed:

- `pyproject.toml`
- `family_menu/src/family_menu/__init__.py`
- `family_menu/src/family_menu/__main__.py`
- `family_menu/src/family_menu/app.py`
- `family_menu/src/family_menu/config.py`
- `family_menu/src/family_menu/db.py`
- `family_menu/src/family_menu/migrations.py`
- `family_menu/src/family_menu/schemas.py`
- `family_menu/src/family_menu/store.py`
- `tests/test_api.py`
- `tests/test_catalog.py`

Tasks:

- Create Python package and local run entry point.
- Add FastAPI app factory with `/health`.
- Add configurable SQLite database path.
- Add explicit schema initialization/migration path.
- Add Pydantic schemas for meals, variation dimensions, variation options, preferences, weekly plans, planned meals, and meal events.
- Add store methods for basic catalog, preferences, weekly plans, and history persistence.

Tests:

- Health endpoint returns app status.
- SQLite schema initializes in an empty database.
- Catalog records can be created, listed, updated, archived, and restored.
- Variation dimensions and options can be created, listed, updated, archived, and restored.
- Preferences are created with sensible defaults.

Exit criteria:

- The backend starts locally.
- The database persists across restarts.
- Tests cover the core schema and CRUD behavior.

## Phase 2: Starter Catalog Import

Files likely changed:

- `data/generic-starter-meal-catalog.example.json`
- `.gitignore`
- `family_menu/src/family_menu/seed.py`
- `family_menu/src/family_menu/store.py`
- `family_menu/src/family_menu/schemas.py`
- `tests/test_seed.py`

Tasks:

- Add a generic public sample catalog into `data/`.
- Keep real installation-specific seed files ignored by git.
- Implement idempotent seed import by meal id, dimension id, and option id.
- Preserve user-edited fields by default.
- Seed default household preferences.
- Expose an admin/local import endpoint or startup seed helper.

Tests:

- Seed import creates generic sample meals.
- Seed import creates expected variation dimensions and options.
- Re-running seed import does not duplicate records.
- User-edited likability is not overwritten by default.

Exit criteria:

- A fresh database can be populated with the starter catalog.
- Seed import is safe to rerun.

## Phase 3: Recommendation Engine

Files likely changed:

- `family_menu/src/family_menu/recommender.py`
- `family_menu/src/family_menu/store.py`
- `family_menu/src/family_menu/schemas.py`
- `tests/test_recommender.py`

Tasks:

- Implement meal scoring from likability, frequency balance, recency, prep score, leftover score, and variety.
- Implement variation-option scoring per meal dimension from option likability, frequency, and recency.
- Preserve locked planned meals during regeneration.
- Preserve locked variation dimensions during variation regeneration.
- Avoid duplicate top-level meals within the same weekly plan.
- Avoid consecutive leftover-style repetition when alternatives exist.
- Return reason codes for meal and option suggestions.

Tests:

- Generated plans contain five distinct meals when enough active meals exist.
- High-likability meals appear more often over repeated simulated weeks than low-likability meals.
- Recently eaten meals are penalized.
- Underused meals are boosted.
- Underused variation options are boosted within the selected meal and dimension.
- Locked meals and locked variation dimensions survive regeneration.
- Skipped meals do not count as eaten.

Exit criteria:

- The recommendation service can explain its selections.
- History changes both meal and variation-option suggestions.

## Phase 4: Weekly Planning API

Files likely changed:

- `family_menu/src/family_menu/app.py`
- `family_menu/src/family_menu/store.py`
- `family_menu/src/family_menu/recommender.py`
- `family_menu/src/family_menu/schemas.py`
- `tests/test_api.py`
- `tests/test_history.py`

Tasks:

- Add weekly plan endpoints.
- Add generate/regenerate endpoints.
- Add manual planned-meal create, patch, replace, reorder, lock, and variation-selection behavior.
- Add mark eaten and skip endpoints.
- Store meal events with variation selections at the time of eating.
- Add current-week lookup based on configured week start day.

Tests:

- Current-week plan can be created and fetched.
- Generate fills the default five dinner slots.
- Replace meal changes meal and resets incompatible variation selections.
- Reorder preserves selected variation options.
- Mark eaten creates a meal event.
- Skip does not create an eaten event.

Exit criteria:

- The backend supports the complete weekly planning workflow independent of the frontend.

## Phase 5: Angular App Shell And Shared Frontend API

Files likely changed:

- `family_menu/src/family_menu/app.py`
- `family_menu/src/family_menu/static/.gitkeep`
- `frontend/angular.json`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/tsconfig.json`
- `frontend/tsconfig.app.json`
- `frontend/tsconfig.spec.json`
- `frontend/src/index.html`
- `frontend/src/main.ts`
- `frontend/src/styles.css`
- `frontend/src/app/app.component.ts`
- `frontend/src/app/app.routes.ts`
- `frontend/src/app/core/api.service.ts`
- `frontend/src/app/core/models.ts`

Tasks:

- Scaffold an Angular app under `frontend/`.
- Use standalone components and Angular routing.
- Use Angular Material for the app shell's primary controls, navigation, form fields, cards, chips, icons, loading states, and dialogs.
- Define typed frontend models matching backend schemas.
- Add an Angular API service for backend calls.
- Configure production build output so FastAPI can serve the built app from `/`.
- Add primary navigation for Weekly Plan, Meal Catalog, Grocery and Prep, History, and Settings.
- Add shared loading, error, empty, and save-failure states.
- Use a practical, compact Material-based layout that works on desktop and phone-sized viewports.

Manual checks:

- App shell loads from local backend.
- Angular dev server can proxy or call the local FastAPI backend during development.
- Navigation works without full page reload.
- Basic loading and error states are visible.

Exit criteria:

- The Angular app shell is ready for screen implementation and can be built into assets served by FastAPI.

## Phase 6: Weekly Plan Screen

Files likely changed:

- `frontend/src/app/weekly-plan/*`
- `frontend/src/app/core/api.service.ts`
- `frontend/src/app/core/models.ts`
- `frontend/src/styles.css`
- Backend endpoints from Phase 4 as needed.
- `tests/test_api.py`

Tasks:

- Render current week and dinner slots.
- Generate suggestions.
- Regenerate unlocked meals.
- Lock/unlock meals.
- Replace top-level meals.
- Reorder meals.
- Render variation dimensions and selected options.
- Swap individual variation options.
- Lock variation dimensions.
- Mark eaten and skip.
- Show suggestion reason codes.
- Show leftover-style warnings when adjacent meals are similar.

Manual checks:

- Generate a plan.
- Replace a meal.
- Swap only one variation dimension such as sauce, base, default protein, diet-compatible protein, vegetables, or prep method where applicable.
- Reorder a meal and confirm option selections remain.
- Mark eaten and confirm history is updated.
- Check desktop and phone-sized layouts.

Exit criteria:

- The main planning workflow is usable.

## Phase 7: Meal Catalog Screen

Files likely changed:

- `frontend/src/app/meal-catalog/*`
- `frontend/src/app/core/api.service.ts`
- `frontend/src/app/core/models.ts`
- `frontend/src/styles.css`
- Catalog API/store methods as needed.
- `tests/test_catalog.py`

Tasks:

- Render active and archived meals.
- Add search and filters.
- Edit meal fields and meal likability.
- Add/edit/archive/restore variation dimensions.
- Add/edit/archive/restore variation options.
- Edit option likability and option metadata.
- Duplicate a meal if time allows; otherwise defer with spec-compatible UI placement.

Manual checks:

- Change meal likability.
- Add a new sauce option to a generic sample meal.
- Add a new vegetable option to a generic sample meal.
- Archive a variation option and confirm it no longer appears in Weekly Plan suggestions.

Exit criteria:

- The user can maintain the catalog without editing JSON.

## Phase 8: Grocery And Prep Screen

Files likely changed:

- `family_menu/src/family_menu/app.py`
- `family_menu/src/family_menu/store.py`
- `family_menu/src/family_menu/schemas.py`
- `frontend/src/app/grocery-prep/*`
- `frontend/src/app/core/api.service.ts`
- `frontend/src/app/core/models.ts`
- `frontend/src/styles.css`
- `tests/test_grocery_prep.py`

Tasks:

- Aggregate shared meal ingredients.
- Aggregate variation-option ingredient additions.
- Group grocery list by broad category when possible.
- Show source meal and option for each item.
- Generate Sunday prep tasks from meal and option prep-ahead data.
- Add custom grocery/prep checklist items for a weekly plan.
- Persist checked state for the plan.

Tests:

- Grocery/prep endpoint includes shared and option-specific ingredients.
- Duplicate ingredient names merge when safe.
- Custom and checked checklist state persists.

Manual checks:

- Open Grocery and Prep for a generated week.
- Confirm pasta/sauce/protein options affect the grocery list.
- Check off items and reload.

Exit criteria:

- The Sunday shopping and prep workflow is usable.

## Phase 9: History Screen

Files likely changed:

- `family_menu/src/family_menu/app.py`
- `family_menu/src/family_menu/store.py`
- `frontend/src/app/history/*`
- `frontend/src/app/core/api.service.ts`
- `frontend/src/app/core/models.ts`
- `frontend/src/styles.css`
- `tests/test_history.py`

Tasks:

- Render recent meal events.
- Show meal frequency, last eaten, expected versus actual usage.
- Show variation-option frequency and last used by meal/dimension.
- Add manual meal event creation.
- Edit/delete mistaken events.
- Filter by meal, option, date range, tag, or feedback.

Tests:

- Meal event history includes selected variation options.
- Manual edits affect future recommendation inputs.
- Deleting an event removes it from scoring inputs.

Manual checks:

- Answer "when did we last have this meal?"
- Answer "when did we last use this variation option?"
- Confirm a history edit changes later suggestions.

Exit criteria:

- History explains recommendation behavior at meal and option levels.

## Phase 10: Family Config, Settings, Import, And Export

Files likely changed:

- `family_menu/src/family_menu/app.py`
- `family_menu/src/family_menu/store.py`
- `frontend/src/app/settings/*`
- `frontend/src/app/core/api.service.ts`
- `frontend/src/app/core/models.ts`
- `frontend/src/styles.css`
- `tests/test_api.py`
- `tests/test_seed.py`

Tasks:

- Render and edit household members, servings, and dietary profiles.
- Choose separate-variation mode or common-compatible-only mode.
- Render and edit household defaults.
- Edit recommendation weights at a basic level.
- Export complete app data to portable JSON.
- Defer import app data with explicit overwrite/merge behavior to a follow-up portability pass.
- Show database path and app version.

Tests:

- Household members and dietary profiles persist.
- Mixed-diet mode applies to newly generated plans.
- Settings changes apply to new plans without rewriting old plans.
- Export includes catalog, dimensions, options, plans, events, and preferences.
- Import merge behavior is documented as deferred.

Manual checks:

- Configure multiple dietary profiles and switch between mixed-diet modes.
- Change default dinner count for future weeks.
- Export data.
- Confirm import is not presented as a shipped v1 action.

Exit criteria:

- Local data is portable and recoverable.

## Phase 11: Verification And Polish

Files likely changed:

- App, tests, and specs as defects or gaps are found.
- `README.md`

Tasks:

- Run full pytest suite.
- Run Angular build and focused frontend tests if configured.
- Run the app locally.
- Browser-check the five screens on desktop and phone-sized viewports.
- Fix layout overlap, unreadable text, and broken states.
- Update README with local setup, run, seed, backup, and restore instructions.
- Update specs if implementation reveals product gaps.

Commands expected:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest -q
cd frontend
npm install
npm run build
cd ..
.venv/bin/python -m family_menu
```

Manual verification:

- Generate a five-meal plan.
- Replace one top-level meal.
- Swap independent variation options for generic sample meals.
- Lock two meals and one variation dimension, then regenerate.
- Mark a meal eaten.
- Confirm History and future suggestions reflect meal and option usage.
- Confirm Grocery and Prep reflects selected options.

Exit criteria:

- The app is usable locally end to end.
- Tests pass.
- Known gaps are documented.

## Risks And Mitigations

- Recommendation tuning may feel too opaque.
  Mitigation: return reason codes and keep manual replacement easy.

- Variation dimensions can become visually dense.
  Mitigation: show compact grouped controls in Weekly Plan and fuller editing in Meal Catalog.

- Grocery quantities are intentionally omitted in v1.
  Mitigation: preserve source meal/option context so the list remains useful without exact quantities.

- Angular adds build tooling and dependency management.
  Mitigation: keep Angular isolated under `frontend/`, serve only built assets from FastAPI, and avoid extra frontend state libraries until the app proves they are needed.

- Seed updates could overwrite user edits.
  Mitigation: make seed import idempotent and preserve user-edited fields by default.

- Private household data could accidentally be staged.
  Mitigation: ignore database, private seed, and export files; run a privacy scan before commit.

## Rollout Notes

- First deployment target is local development.
- Database path must be configurable from the start.
- Frontend build artifacts should be generated, not edited by hand.
- Home Assistant packaging should not require a backend rewrite.
- No cloud dependencies should be added.

## SDD Pause Points

- This plan requires explicit approval before implementation starts.
- If implementation discovers that variation dimensions need a different schema, update the specs and this plan before continuing.
- If Angular introduces deployment friction that changes the packaging approach, update the plan before changing direction.
