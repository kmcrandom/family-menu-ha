# Plan: Home Assistant Changelog and Read-Only Meal Catalog

## Goal

Apply the MinuteMetrics Home Assistant add-on changelog convention to Family Menu and make the Meal Catalog detail read-only by default until the user explicitly enters edit mode.

## Scope

- Add the Home Assistant add-on changelog file at `family-menu/CHANGELOG.md`.
- Keep the existing root `CHANGELOG.md` content mirrored into the add-on-local changelog for the current release history.
- Add a CI/release validation check that fails when `family-menu/config.yaml` has a version without a matching `family-menu/CHANGELOG.md` entry.
- Update Meal Catalog so existing selected meals are read-only by default.
- Add an Edit action to switch the selected meal detail into edit mode.
- Keep create/duplicate behavior prepared to open in edit mode, even if create/duplicate controls are not currently exposed.

## Implementation Steps

1. Add add-on changelog
   - Create `family-menu/CHANGELOG.md`.
   - Use the MinuteMetrics style: add-on-local title and version headings without dates.
   - Copy the current release entries from root `CHANGELOG.md`, preserving user-visible bullets.

2. Add changelog validation
   - Add a small test or script that reads `family-menu/config.yaml` and asserts `family-menu/CHANGELOG.md` contains a heading for that exact version.
   - Prefer a focused pytest under `tests/` if the existing backend test suite already runs in CI.
   - Confirm the current version `0.1.4` passes.

3. Update Meal Catalog state
   - Add an `isEditing` flag to `MealCatalogComponent`.
   - Make `selectMeal` reset `isEditing` to `false` for existing meals.
   - Add `startEditing`, `cancelEditing`, and a helper for selecting/reloading while preserving the desired edit state.
   - After saving an existing meal, reload the meal and return to read-only mode.
   - Keep mutation handlers for archive/restore, dimensions, options, and add-option guarded so they do nothing when not in edit mode.

4. Update Meal Catalog template
   - Change the page copy from always-edit language to catalog review/manage language.
   - Show an Edit button in read-only mode.
   - Show Save and Cancel in edit mode.
   - Disable or hide direct mutation controls while read-only.
   - Render form controls disabled in read-only mode, or use read-only display where Angular Material controls do not support read-only cleanly.
   - Keep the source open-link action available in both modes.

5. Update styling
   - Add compact styling for a read-only state banner or mode indicator if needed.
   - Ensure disabled/read-only controls remain legible in the dark theme.
   - Verify mobile layout does not introduce overlapping actions.

## Verification

- Run backend tests, including the new changelog/version check.
- Run the Angular build.
- Browser-check Meal Catalog on desktop:
  - selecting an existing meal opens read-only
  - Edit enables fields and option controls
  - Save returns to read-only after reload
  - selecting another meal returns to read-only
  - source link remains usable in read-only mode
- Browser-check Meal Catalog on a phone-sized viewport for action wrapping and disabled/read-only legibility.

## Risks and Notes

- The current Meal Catalog does not expose create or duplicate buttons, so implementation will prepare the component state helpers for edit-on-create/duplicate without adding those broader workflows.
- Angular Material disabled form fields may reduce contrast; styling may be needed to keep read-only content legible.
- Option edits currently save immediately on change. Gating these controls behind edit mode prevents accidental mutation in read-only mode without redesigning option editing into a draft/save flow.
