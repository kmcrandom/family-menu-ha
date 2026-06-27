# Plan: Variation Colors and Ingredient Amounts

## Goal

Add muted semantic color accents for variation dimensions across Weekly Plan and Meal Catalog, and add ingredient amounts/units from recipe editing through Grocery and Prep output.

## Implementation Steps

1. Backend ingredient model
   - Add an `IngredientItem` schema with `label`, `amount`, `unit`, `category`, and `note`.
   - Update `Meal`, `MealPatch`, `VariationOption`, `VariationOptionCreate`, and `VariationOptionPatch` so `shared_ingredients` and `ingredient_additions` accept structured ingredient items while remaining backward-compatible with legacy strings.
   - Keep `ingredient_omissions` as label strings because omissions match by ingredient label only.
   - Store structured ingredients in the existing JSON columns; no new SQLite columns are expected.

2. Normalization and import compatibility
   - Add store helpers to normalize ingredient arrays:
     - legacy string -> `{ label: string }`.
     - structured object -> cleaned `IngredientItem`.
     - blank labels are ignored.
   - Normalize on seed import, API response, and patch/create paths.
   - Preserve current private DB data by interpreting existing string arrays safely.

3. Grocery aggregation with amounts
   - Update `grocery_prep` to aggregate ingredient items rather than only labels.
   - Use ingredient `label` for dedupe and omission matching.
   - Show amount/unit in generated grocery rows.
   - Add a conservative amount parser that supports integers, decimals, fractions, and mixed numbers.
   - Add a unit-family converter for:
     - weights: pounds, ounces, and grams.
     - volumes: milliliters, liters, teaspoons, tablespoons, and cups.
     - counts: blank or each-style units for simple amounts such as `5 carrots`.
   - Sum amounts when both amounts are numeric and units are compatible within the same family.
   - Prefer a readable output unit based on the family and amount, such as cups for larger volumes, tablespoons/teaspoons for smaller volumes, pounds/ounces for imperial weights when the source uses imperial units, or grams when the source uses metric-only units.
   - If amounts are missing, text-based, or incompatible, preserve readable per-source amount details instead of guessing.
   - Keep category inference from label unless an ingredient item supplies `category`.

4. API and frontend model updates
   - Add TypeScript `IngredientItem`.
   - Update meal and option models so ingredient fields use `IngredientItem[]`.
   - Extend `GroceryPrepItem` with optional amount/unit/display metadata needed by the list.

5. Meal Catalog ingredient editing
   - Replace the current plain line parsing for shared ingredients and option additions with an amount-aware line format.
   - Use a compact, readable line format such as:
     - `2 cups rice`
     - `1.5 lb vegetables | sliced`
     - `to taste salt`
   - Convert lines to structured ingredient items on save and back to text on load.
   - Keep grocery omissions as one label per line.
   - Keep the editor compact on desktop/tablet and stacked on phone.

6. Variation color semantics
   - Add shared CSS classes for muted variation colors by dimension key:
     - primary protein, diet protein, vegetables, sauce, base/starch, toppings, prep method, and fallback.
   - Add Angular helpers that map a variation dimension key to a stable CSS class.
   - Apply the color treatment to Weekly Plan variation controls.
   - Apply the same treatment to Meal Catalog variation dimension cards and option editors.
   - Preserve readable labels, dark-mode contrast, disabled states, and mobile layout.

7. Tests
   - Add backend tests for:
     - legacy string ingredients remain accepted and returned in normalized form.
     - structured meal and option ingredients appear in Grocery and Prep with amounts.
     - compatible weight amounts sum across pounds, ounces, and grams.
     - compatible volume amounts sum across milliliters, liters, teaspoons, tablespoons, and cups.
     - fractional and mixed-number amounts are parsed and summed.
     - simple count amounts, such as repeated carrot counts, are summed.
     - incompatible or text amounts preserve per-source amount details.
     - omissions still match by label after structured ingredient conversion.
   - Update existing grocery/prep tests for the new normalized response shape.

8. Browser verification
   - Run `npm run build`.
   - Run `.venv/bin/python -m pytest -q`.
   - Browser-check Weekly Plan and Meal Catalog for muted variation colors at desktop/tablet/phone widths.
   - Browser-check Meal Catalog amount editing renders and remains compact.
   - Browser-check Grocery + Prep displays amounts without overflow.
   - Verify no console errors and no horizontal overflow.

## Risks and Notes

- Parsing free-form ingredient lines is imperfect. The first parser should be conservative and preserve unclear text as the label rather than inventing wrong amounts.
- Exact grocery quantity math is intentionally limited to compatible unit families. It does not convert between weight and volume or infer density.
- Existing checklist state is keyed mostly by label/category/source today. Adding amount display should not break checked-state persistence for the same label/source.
- Existing private catalog data may contain string ingredients. Normalization must not erase or corrupt those values.
- Color accents must stay muted and semantic; they should help scanning without becoming the dominant visual palette.

## Non-Goals

- Full recipe scaling by serving count.
- Cross-family unit conversion, such as cups to ounces by ingredient density.
- Nutrition tracking.
- Pantry inventory.
- Drag-and-drop ingredient rows.
- Exact parser support for every natural-language ingredient phrase.
