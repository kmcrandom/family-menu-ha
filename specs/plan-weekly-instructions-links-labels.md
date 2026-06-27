# Plan: Weekly Instructions, Recipe Links, and Catalog Labels

## Goal

Make Weekly Plan meal rows more compact, add recipe/source links and cooking instructions, and move meal labels/tags into Meal Catalog as selectable filters.

## Implementation Steps

1. Backend meal source fields
   - Add `source_url` and `source_name` to the `meals` table with migration-safe `_ensure_columns` additions.
   - Add `source_url` and `source_name` to `Meal` and `MealPatch` schemas.
   - Include source fields in store read, patch, import, and export paths.
   - Preserve existing local catalogs by defaulting new fields to blank values.

2. Meal instructions persistence
   - Confirm meal-level `instructions` already persists through schema, store, and seed import paths.
   - Add or update backend tests that patch and reload `source_url`, `source_name`, and `instructions`.
   - Keep variation-option `instructions` available for the Weekly Plan dialog when selected options have notes.

3. Frontend models and API typing
   - Add optional `source_url` and `source_name` to the TypeScript `Meal` model.
   - Confirm `instructions` is present on `Meal` and `VariationOption`.
   - Keep API endpoints unchanged; use existing meal patch/read routes.

4. Meal Catalog source, instructions, and labels
   - Add form controls for source URL, source name, instructions text, and tags/labels text.
   - Show an external-link button when `source_url` is present.
   - Convert instructions between line-based textarea text and `string[]`.
   - Convert tags between compact line/comma text and `string[]`, preserving existing tag search behavior.
   - Add a compact tag/label chip filter near the search field.
   - Selecting a chip filters the meal list by that tag; clearing the selected chip returns to normal search results.
   - Keep catalog layout compact on desktop/tablet and stacked on phone.

5. Weekly Plan compact variation row layout
   - Remove the duplicate selected-variation summary paragraph below the meal picker.
   - Keep each variation control horizontally ordered as:
     - dimension label
     - dropdown option select
     - icon-only lock/unlock button
   - Replace visible `lock` text in variation controls with a Material lock icon button.
   - Add clear tooltips and accessible labels for locked/unlocked variation buttons.
   - Keep existing meal-level lock behavior, with the visible row button allowed to remain unless the implementation naturally improves it without extra scope.

6. Weekly Plan source link and instructions dialog
   - Add a compact source-link action to each meal row when `source_url` is set.
   - Add a compact instructions action to each meal row.
   - Implement a Material dialog that shows:
     - meal name
     - meal instructions
     - selected variation option instructions when present
     - source link/source name when present
   - Show a useful empty state in the dialog if a meal has no instructions yet.
   - Ensure the dialog is readable on desktop and phone-sized viewports.

7. Private recipe-link enrichment
   - Use web lookup during implementation to find high-quality recipe/reference links for the local meals in this installation.
   - Prefer stable, reputable recipe pages with clear cooking steps.
   - Populate `source_url`, `source_name`, and concise rewritten cooking instructions in the ignored local SQLite database or an ignored local helper artifact.
   - Do not add the household's selected recipe links or generated instructions to tracked starter catalog/spec files.
   - Keep final reporting generic; do not echo private meal names or recipe choices unless needed for troubleshooting.

8. Tests
   - Add backend tests for source URL/name and instructions patch/reload.
   - Add or update frontend build checks for new model/template bindings.
   - Add focused parser/helper tests only if tag or instruction conversion logic is moved into testable helpers; otherwise verify through browser checks.

9. Browser verification
   - Run `npm run build`.
   - Run `.venv/bin/python -m pytest -q`.
   - Browser-check Weekly Plan on desktop/tablet and phone widths:
     - no duplicate variation summary under meal picker
     - variation label/select/lock icon stay compact and readable
     - instructions dialog opens and fits
     - source link action appears only where configured
   - Browser-check Meal Catalog:
     - source URL/name and instructions are visible/editable
     - tag/label chips are visible and filter the meal list
     - selected tag filter can be cleared
   - Check for console errors and horizontal overflow.
   - Run the existing privacy scan over tracked candidate files before finishing.

## Risks and Notes

- Recipe websites vary widely in structure. The implementation should summarize instructions conservatively and keep the original link available instead of attempting perfect recipe import.
- Web lookup can introduce private meal-specific data. That data must stay local/ignored.
- Source links may not exist for every meal template. The UI should handle missing links gracefully.
- Tags currently live as meal `tags`; the UI can label them as labels/tags without adding a new table or field.
- Weekly Plan row density should improve without making phone layout cramped.

## Non-Goals

- Full automated recipe scraping as a reusable service.
- Copying full third-party recipe text into the app.
- Recipe scaling by servings.
- Nutrition data.
- A new public cloud sync or account system.
- A separate label taxonomy table; V1 uses existing meal `tags`.
