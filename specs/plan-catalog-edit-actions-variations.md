# Plan: Meal Catalog Edit Actions and Variations

## Goal

Refine Meal Catalog editing so the selected meal header owns the edit actions, remove the duplicate source URL open button, and let users add or remove variation dimensions while editing, including reusable variation types and color selection.

## Implementation Steps

1. Header action states
   - Update `meal-catalog.component.html` so read-only mode shows the header source-link action, Archive or Restore, and Edit.
   - Update edit mode so the same header action area shows Save and Cancel only.
   - Move the existing Save Meal and Cancel actions out of the bottom form action row.
   - Keep `archiveMeal()` available only from read-only mode and remove the current `isEditing` guard that blocks it.
   - Add a popup confirmation before archiving an active meal from read-only mode.
   - Allow restoring an archived meal from read-only mode without confirmation.
   - Keep `saveMeal()` available only in edit mode and preserve the existing save/reload behavior.
   - Keep `cancelEditing()` restoring saved selected-meal values and returning to read-only mode.

2. Remove duplicate source URL action
   - Remove the icon button beside the Source URL form field.
   - Simplify `.source-url-row` styling so the Source URL field uses normal form-grid width.
   - Keep the selected-meal header source-link icon when a source URL exists.

3. Variation dimension color data
   - Add optional `color` to backend `VariationDimension`, `VariationDimensionCreate`, and `VariationDimensionPatch`.
   - Add a nullable `color` column to `variation_dimensions` through migrations and `_ensure_columns`.
   - Include `color` in seed import, full import/export, create, patch, and response paths.
   - Add `color?: string | null` to the frontend `VariationDimension` model.
   - Preserve existing behavior for dimensions without a stored color by using key-derived semantic fallback styles.

4. Variation dimension add/remove API usage
   - Add frontend API methods for `createDimension`, `archiveDimension`, and `restoreDimension` using existing backend endpoints.
   - Use archive as the remove action from Meal Catalog editing.
   - Preserve current option archive/restore behavior.

5. Reusable variation type suggestions
   - Add frontend helpers that collect reusable variation types from all loaded meals plus built-in defaults:
     - primary protein
     - pescatarian or diet-compatible protein
     - vegetables
     - sauce
     - starch/base
     - toppings
     - prep method
   - Filter suggestions to exclude active variation dimensions already present on the selected meal by key.
   - Sort suggestions in a stable, readable order with built-ins first and catalog-discovered custom types after.

6. Add custom variation type and color controls
   - Add edit-mode controls above or near the variation dimension stack for:
     - choosing a reusable variation type
     - entering a custom variation name/key
     - selecting required/optional
     - selecting a color
   - Show a preset Material Design color palette as swatches.
   - Hide or disable preset colors already used by active variation dimensions on the selected meal.
   - Include an `<input type="color">` custom color picker.
   - Generate a stable `variation_...` key from custom names, while allowing the generated key to be adjusted before adding.

7. Variation remove and edit controls
   - Show remove/archive dimension controls only while editing.
   - Add a confirmation before archiving a dimension that has options.
   - Show color controls on each dimension while editing, and patch `color` changes immediately like existing required toggles.
   - Apply stored color to Meal Catalog dimension cards and Weekly Plan variation controls through CSS custom properties, falling back to existing semantic classes.

8. Backend tests
   - Add or update tests for:
     - creating a variation dimension with `color`
     - patching a dimension color
     - archiving a dimension removes it from non-archived meal responses and new recommendation candidates
     - import/export preserves `color`
     - legacy databases without a color column are upgraded

9. Frontend verification
   - Run `npm run build`.
   - Run `.venv/bin/python -m pytest -q`.
   - Browser-check Meal Catalog desktop:
     - read-only header shows Archive/Edit
     - Archive opens a confirmation popup before archiving
     - edit header shows Save/Cancel and hides Archive
     - Source URL field has no duplicate open icon
     - adding a reusable dimension excludes existing types
     - adding a custom variation with a preset/custom color renders the colored dimension
     - removing a dimension archives it from active planning/editing surfaces
   - Browser-check Meal Catalog phone width for no overlap, no horizontal overflow, and usable color/add controls.
   - Browser-check Weekly Plan enough to confirm stored/custom variation colors still render without breaking fallback semantic colors.

## Risks and Notes

- Existing planned meals and history may reference archived dimensions. Archiving rather than deleting preserves those references.
- Stored custom colors must have enough dark-mode contrast. The first implementation should use color as a border/background accent and retain text labels.
- Adding a dimension with a reused key may conflict with an archived dimension id for the same meal. Implementation should either restore/update the archived dimension or generate a unique id safely.
- The current store creates dimension ids from meal id and key. The implementation should handle collisions cleanly instead of failing with a raw SQLite error.
- Color filtering is scoped to the selected meal, not the entire catalog, so the same color can still be reused on different meals.

## Non-Goals

- Hard-deleting variation dimensions.
- Drag-and-drop reordering of dimensions.
- Multi-select variation dimensions.
- Bulk copying options from another meal's variation dimension.
- Advanced color contrast tuning beyond safe muted accent rendering.
