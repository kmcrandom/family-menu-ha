# Plan: Meal Catalog Grocery and Prep Editing

## Goal

Expose the meal catalog fields that generate Grocery and Prep so a user can see and edit grocery ingredients and Sunday prep tasks without editing JSON or seed files.

## Implementation Steps

1. Meal-level editor fields
   - Add editable line-based fields to the Meal Catalog form for:
     - `shared_ingredients`
     - `prep_ahead`
   - Convert textarea lines to trimmed string arrays on save.
   - Convert existing string arrays back to newline-separated text when selecting a meal.
   - Keep existing meal fields and save behavior intact.

2. Variation-option editor fields
   - Expand each option row or add a compact option detail area with line-based editors for:
     - `ingredient_additions`
     - `ingredient_omissions`
     - `prep_ahead`
   - Save option edits through the existing `patchOption` API.
   - Preserve existing option name, likability, archive/restore, and add-option behavior.

3. UI clarity
   - Label meal-level fields as affecting every planned instance of the meal.
   - Label option-level fields as affecting Grocery and Prep only when that option is selected.
   - Use Angular Material form fields, textareas, buttons, and compact cards consistent with the current dark UI.
   - Avoid raw JSON editing.

4. Verification
   - Run `npm run build`.
   - Run the backend test suite.
   - Browser-check Meal Catalog:
     - Shared ingredients and Sunday prep tasks are visible for a selected meal.
     - Editing meal-level fields saves and reloads correctly.
     - Option-level ingredient additions and prep tasks are visible and editable.
   - Browser-check Grocery and Prep:
     - A saved meal-level ingredient/prep edit appears for a week containing that meal.
     - A saved option-level ingredient/prep edit appears when that option is selected.

## Risks and Notes

- Existing local catalog data is private user data, so browser verification should avoid mentioning real meal names in final output.
- `ingredient_omissions` is already stored but not currently used by grocery aggregation. It should still be editable for completeness and future filtering, but this plan does not change grocery aggregation semantics.
- Textarea ordering should be preserved in saved arrays even though the generated grocery list may sort by category and label.

## Non-Goals

- Exact quantities, units, or grocery store departments beyond the current category heuristic.
- Pantry inventory or hiding pantry staples.
- Changing the grocery aggregation algorithm except for consuming edits already supported by the existing model.
