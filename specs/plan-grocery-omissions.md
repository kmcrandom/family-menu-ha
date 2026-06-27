# Plan: Grocery Ingredient Omissions

## Goal

Make variation-option `ingredient_omissions` affect generated Grocery and Prep output by removing matching meal-level shared ingredients for the planned meal where the option is selected.

## Implementation Steps

1. Grocery aggregation
   - Update `Store.grocery_prep` so it gathers selected option omissions before adding meal-level shared ingredients.
   - Match omissions against shared ingredient labels using trimmed, case-normalized text.
   - Skip omitted shared ingredients for that planned meal.
   - Continue adding selected option `ingredient_additions`, option `value` ingredients, and prep tasks after omissions are applied.

2. Source preservation
   - Keep existing deduplication and source merging behavior.
   - Ensure omissions for one meal do not remove the same ingredient if another planned meal or selected option still contributes it.

3. Meal Catalog UI copy
   - Update the Grocery omissions hint to explain that these lines remove matching shared ingredients when the option is selected.

4. Verification
   - Add backend tests for:
     - An option omission removes a matching meal-level shared ingredient.
     - Omission matching is trim/case-insensitive.
     - An omitted ingredient still appears if another planned meal or selected option contributes it.
   - Run the full backend test suite.
   - Run `npm run build`.
   - Browser-smoke Meal Catalog to confirm the updated hint renders without console errors.

## Risks and Notes

- The omission model is label-based, so near-duplicates such as `cheddar cheese` and `shredded cheddar` will not be treated as the same ingredient.
- Checklist checked state is keyed by label/category/source. Removing an omitted item from generated output means any old checked state for that item may remain stored but will not display unless the item appears again.
- This does not implement quantities or partial reductions.

## Non-Goals

- Fuzzy ingredient matching.
- Quantity math.
- Omitting option-added ingredients.
- Omitting prep tasks.
