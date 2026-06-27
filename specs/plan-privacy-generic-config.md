# Privacy And Generic Family Config Implementation Plan

## Scope

Update the existing local Family Menu app so the repository is safe to publish without personal household details while preserving the current local installation's meal catalog and database.

This plan covers:

- Keeping private SQLite databases, local seed catalogs, and exports out of git.
- Replacing tracked concrete starter data with generic sample data.
- Preserving the current local installation's existing `family-menu.db` and current selected meals.
- Adding Family Config for household members, serving counts, dietary profiles, and mixed-diet recommendation mode.
- Updating backend, frontend, tests, and docs to use generic terms instead of a specific household composition or fixed diet.
- Verifying no private household-specific data is staged.

## Non-Scope

- Cloud sync or accounts.
- Public authentication.
- Full import/merge restore flow.
- Nutrition, allergens, macros, or medical diet advice.
- Rewriting the existing local database contents unless a migration is required.
- Removing the user's private local catalog from the working machine.

## Phase 1: Private Data Boundary And Git Hygiene

Files likely changed:

- `.gitignore`
- `README.md`
- `specs/deployment-packaging.md`
- `specs/starter-meal-catalog.md`
- `specs/verification.md`

Tasks:

- Ignore private local seed/catalog files, including `data/starter-meal-catalog.json`, `data/local-*.json`, `data/private-*.json`, and app exports.
- Keep `family-menu.db`, `*.db`, and generated frontend build assets ignored.
- Add a generic tracked sample catalog path, such as `data/generic-starter-meal-catalog.example.json`.
- Document the default DB path and how to override it with environment variables.
- Document that personal meal catalogs and exported backups are private local data.

Tests and checks:

- `git status --short --ignored` confirms `family-menu.db` and the private seed catalog are ignored.
- Privacy scan of candidate tracked files finds no relationship-specific terms or private meal list.

Exit criteria:

- A future commit can stage source/spec files without staging the user's private DB or selected-meal catalog.

## Phase 2: Generic Public Starter Catalog

Files likely changed:

- `data/generic-starter-meal-catalog.example.json`
- `specs/starter-meal-catalog.json`
- `family_menu/src/family_menu/config.py`
- `family_menu/src/family_menu/store.py`
- `tests/test_seed.py`
- `tests/test_catalog.py`
- `tests/test_grocery_prep.py`

Tasks:

- Replace tracked public seed data with a small generic sample catalog.
- Change default seed path from `data/starter-meal-catalog.json` to the generic example file.
- Preserve support for `FAMILY_MENU_SEED` so this installation can continue using a private local seed file if needed.
- Update tests so they use generic meal ids, generic variation dimensions, and generic ingredient labels.
- Keep the current `family-menu.db` untouched so the local app retains the user's selected meals.

Tests and checks:

- Seed import creates generic sample meals and dimensions.
- Seed import remains idempotent.
- Existing user-modified fields remain preserved by seed import.
- JSON validation passes for generic sample data.

Exit criteria:

- Fresh installs get generic sample data.
- This local install still uses the existing ignored database unless the user chooses to reset it.

## Phase 3: Backend Family Config Data Model

Files likely changed:

- `family_menu/src/family_menu/migrations.py`
- `family_menu/src/family_menu/schemas.py`
- `family_menu/src/family_menu/store.py`
- `family_menu/src/family_menu/app.py`
- `tests/test_api.py`
- `tests/test_recommender.py`

Tasks:

- Add `household_members` and `dietary_profiles` tables.
- Add preference fields for `mixed_diet_mode`, defaulting to `separate_variations`.
- Add schemas for household config, members, and dietary profiles.
- Add API endpoints:
  - `GET /api/v1/household`
  - `PATCH /api/v1/household`
  - `POST /api/v1/household/members`
  - `PATCH /api/v1/household/members/{member_id}`
  - `POST /api/v1/household/dietary-profiles`
  - `PATCH /api/v1/household/dietary-profiles/{profile_id}`
- Rename public API/model fields away from household-specific terms where practical, while preserving backward-compatible seed import for old private catalog keys.
- Include database path and seed path in a local-only settings/status response.

Tests:

- Default household config can be created and fetched.
- Household members can be added, edited, archived, and restored or deactivated.
- Dietary profiles can be added and edited.
- `mixed_diet_mode` persists.
- Existing database migrations preserve meal catalog, weekly plans, history, and checklist state.

Exit criteria:

- Backend supports generic Family Config without losing existing local data.

## Phase 4: Dietary Compatibility Recommendation Behavior

Files likely changed:

- `family_menu/src/family_menu/recommender.py`
- `family_menu/src/family_menu/store.py`
- `family_menu/src/family_menu/schemas.py`
- `tests/test_recommender.py`

Tasks:

- Add diet compatibility helpers based on meal/option diet tags and dietary profile rules.
- In `common_compatible_only` mode, filter meals and required options that conflict with any active profile.
- In `separate_variations` mode, require each active diet profile to have a compatible option for diet-sensitive required dimensions where applicable.
- Keep recommendation reason codes generic.
- Preserve the existing variation-selection model for this local install, including old private dimensions, while introducing generic names for new public data.

Tests:

- Common-compatible mode excludes incompatible meals/options.
- Separate-variation mode selects compatible options for multiple configured profiles.
- Underused option scoring still works within compatibility constraints.
- Not enough compatible meals returns a useful shortage state.

Exit criteria:

- Meal suggestions respect Family Config mode without hardcoding any particular diet or relationship.

## Phase 5: Angular Family Config UI

Files likely changed:

- `frontend/src/app/app.ts`
- `frontend/src/app/app.routes.ts`
- `frontend/src/app/core/models.ts`
- `frontend/src/app/core/api.service.ts`
- `frontend/src/app/settings/*`
- Potentially `frontend/src/app/family-config/*`
- `frontend/src/styles.css`

Tasks:

- Rename the Settings screen or add a Family Config section.
- Add controls for:
  - Household name.
  - Household members.
  - Dinner servings per member.
  - Leftover lunch servings per member.
  - Dietary profile assignment.
  - Dietary profile creation/editing.
  - Mixed-diet mode.
- Show local DB path and seed path as local status information.
- Update UI copy from fixed household assumptions to generic household terms.
- Keep existing settings controls for week start, shopping day, dinner count, repeat gap, and recommendation weights.

Manual checks:

- Add/edit a household member.
- Add/edit a dietary profile.
- Switch mixed-diet mode.
- Save and reload.
- Confirm existing weekly plan and catalog screens still load.

Exit criteria:

- A user can configure household size and dietary preferences without editing source files.

## Phase 6: Source Sanitization And Compatibility Cleanup

Files likely changed:

- `family_menu/src/family_menu/migrations.py`
- `family_menu/src/family_menu/schemas.py`
- `family_menu/src/family_menu/store.py`
- `frontend/src/app/core/models.ts`
- `frontend/src/app/meal-catalog/*`
- `frontend/src/app/weekly-plan/*`
- `tests/*`
- `README.md`

Tasks:

- Rename legacy code-facing fields to generic names such as `simple_serving_variations` where practical.
- Keep import compatibility for existing private seed files that still use old keys.
- Rename legacy diet-specific protein fields to generic `alternate_proteins` or compatibility-aware structures where practical.
- Avoid public UI labels that imply one specific household's diet.
- Update tests to assert generic behavior, not specific private meal names.

Tests:

- Backend tests pass.
- Angular production build passes.
- Existing private database can still be opened and served.
- Private seed import compatibility works when `FAMILY_MENU_SEED` points to the old local private catalog.

Exit criteria:

- Tracked source and tests no longer encode private installation catalog choices or household relationships.

## Phase 7: Verification And Privacy Audit

Files likely changed:

- `README.md`
- `specs/verification.md`
- Tests or implementation files found during QA.

Tasks:

- Run backend tests.
- Run Angular build.
- Browser-check Family Config, Weekly Plan, Meal Catalog, Grocery + Prep, History, and Settings on desktop and mobile.
- Run source/privacy scans across staged candidate files.
- Verify ignored private files are still present locally but not staged.
- Confirm current local installation's meal catalog remains available through the existing DB.

Commands expected:

```bash
.venv/bin/python -m pytest -q
cd frontend
npm run build
cd ..
git status --short --ignored
rg -n -i "private household marker|private menu marker" --glob '!frontend/node_modules/**' --glob '!family-menu.db' .
```

Manual verification:

- Open the app locally.
- Confirm Family Config can save household members and diet profiles.
- Confirm the current local install still shows the user's existing catalog from `family-menu.db`.
- Confirm a fresh empty DB seeds only generic sample meals.
- Confirm private files are ignored by git.

Exit criteria:

- Tests pass.
- Browser workflow passes.
- No private household-specific data is staged or included in tracked source.

## Risks And Mitigations

- Existing local catalog uses old field names.
  Mitigation: preserve backward-compatible import and DB response mapping during the rename.

- Common-compatible mode may filter too aggressively.
  Mitigation: return clear shortage explanations and make separate-variation mode easy to choose.

- A private seed file could still appear as untracked before `.gitignore` is updated.
  Mitigation: update `.gitignore` first and verify with `git status --ignored`.

- The current DB may contain private data.
  Mitigation: keep DB files ignored and never stage them; preserve them only as local runtime state.

- Generated frontend build output may contain old strings until rebuilt.
  Mitigation: keep build output ignored and rebuild after UI copy changes.

## SDD Pause Points

- This plan requires explicit approval before implementation starts.
- If the implementation reveals a migration that could alter existing local private data, pause and ask before applying it to the current `family-menu.db`.
- If a privacy scan finds private data in a file that must remain tracked, sanitize that file before continuing.
