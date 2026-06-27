# Plan: Source-Derived Catalog Rebuild

## Goal

Rebuild source-derived catalog fields in the private local meal database from the source links already
attached to meals. Preserve only meal names and links before rebuilding ingredients, instructions, timing,
variations, proteins, and prep tasks. Do not add household-specific recipes, source URLs, or selected meals
to tracked files.

## Scope

- Enrich the ignored local SQLite database only.
- Create a timestamped backup of the current ignored SQLite database before changing it.
- Preserve meal ids, names, source URLs, and source names.
- Clear existing source-derived meal fields before rebuilding:
  - `shared_ingredients`
  - `primary_proteins`
  - `alternate_proteins`
  - `prep_ahead`
  - `instructions`
  - timing and scoring fields where source values are available
  - variation dimensions and options
- Replace meal-level `shared_ingredients` with non-protein source recipe ingredients.
- Add amount, unit, category, and note metadata where parsing is clear.
- Preserve the remaining ingredient text in a readable label or note when parsing is unclear.
- Replace meal-level `instructions` with concise source-derived cooking steps when the linked source
  exposes recipe instructions.
- Keep instructions practical and short enough for the Weekly Plan dialog; do not store full article text
  or unrelated recipe-page content.
- Identify source recipe proteins and create `variation_primary_protein` options. Protein ingredients must
  be stored in each protein option's `ingredient_additions`.
- If the source default protein is not pescatarian-compatible, create a pescatarian-compatible protein
  variation option with conservative editable ingredient additions.
- Identify source recipe substitution points and create variation dimensions/options where useful, such as
  sauce, base/starch, vegetable mix, cheese, toppings, or prep method.
- Store substitution-specific ingredients in the related variation option's `ingredient_additions`.
- Extract prep-ahead tasks from source instructions where practical, including maximum lead time and
  storage guidance.
- Extract active prep time, cook time, total time, tags, make-ahead hints, and leftover style from source
  metadata where possible. Use conservative defaults when unavailable.
- Do not keep old household-added sides, substitutions, or pantry items unless they are present in or
  directly inferred from the linked source recipe. These can be re-added manually after enrichment if desired.
- Keep tracked generic starter catalog files unchanged except for specs and plan documentation.

## Phases

1. Back up and inspect local catalog data
   - Create a timestamped copy of `family-menu.db` before any clearing or writes.
   - Read meals from `family-menu.db`.
   - Identify meals with `source_url`, current ids/names/source names, and existing plans/history that
     reference meal ids.
   - Export a temporary local working summary outside tracked files if useful.

2. Gather source recipe data
   - Use the existing meal `source_url` values.
   - Prefer recipe page structured data for ingredients, instructions, prep time, cook time, total time,
     yield, category, and cuisine.
   - Fall back to page content only when structured data is missing and extraction is clear.
   - Normalize source ingredient lines into structured catalog entries; do not copy full recipe pages.
   - Normalize source instruction steps into concise lines for app display.
   - Identify default proteins, pescatarian compatibility, substitution candidates, and prep-ahead tasks.
   - If a source is unavailable or unclear, leave that meal with its preserved name/link and note the skip.

3. Clear source-derived fields
   - For each source-linked meal, clear shared ingredients, protein lists, prep tasks, instructions, and
     source-derived variation dimensions/options.
   - Preserve meal ids, names, source URLs, source names, status, likability, history, and weekly plan
     references.

4. Apply local database rebuild
   - Replace `meals.shared_ingredients` JSON with structured non-protein ingredient objects derived from
     the linked source.
   - Replace `meals.instructions` JSON with concise source-derived recipe steps.
   - Update meal prep/cook fields from source metadata where available.
   - Create source-derived variation dimensions/options.
   - Store protein and other substitution-specific ingredients in option `ingredient_additions`.
   - Add option diet tags and compatible diet profile hints, including pescatarian options where needed.
   - Add source-derived Sunday prep tasks with lead-time and storage guidance.
   - Preserve meal identity, source, history, and weekly plan references.
   - Do not modify tracked starter catalog JSON with household-specific values.

5. Verify backend behavior
   - Confirm local API returns structured ingredient objects with amounts.
   - Confirm local API returns refreshed instruction steps.
   - Confirm source-derived protein groceries are option additions rather than meal-level shared ingredients.
   - Confirm meals with non-pescatarian source proteins have a pescatarian-compatible protein option.
   - Confirm Grocery + Prep includes amount displays for enriched planned meals.
   - Run backend tests.

6. Verify frontend behavior
   - Build the Angular app.
   - Browser-check Meal Catalog:
     - Shared grocery ingredients show amount lines rather than blanks.
     - Option grocery additions show amount lines when populated.
     - Cooking instructions show refreshed source-derived steps.
     - Prep/cook time fields show source-derived values where available.
   - Browser-check Grocery + Prep:
     - Amounts appear in the grocery list.
     - Compatible duplicate units still aggregate.
     - Switching protein variation changes protein groceries.

7. Privacy and repo hygiene
   - Confirm `family-menu.db` remains ignored.
   - Confirm the timestamped backup remains ignored.
   - Confirm tracked files do not include household-specific source URLs, selected meals, or private recipe
     ingredient details.
   - Summarize enrichment generically without listing private meal names or source URLs.

## Likely Files and Data

- Local ignored data:
  - `family-menu.db`
- Verification and support:
  - `family_menu/src/family_menu/store.py`
  - `frontend/src/app/meal-catalog/meal-catalog.component.ts`
  - `frontend/src/app/grocery-prep/grocery-prep.component.html`
  - `tests/test_grocery_prep.py`
- Tracked documentation:
  - `specs/plan-source-derived-ingredient-amounts.md`

## Risks

- Recipe pages may block automated access or have ingredients embedded in scripts.
- Recipe pages may expose overly long, nested, or promotional instruction text. The enrichment should keep
  concise recipe steps and skip unrelated page content.
- Automated protein/substitution detection is heuristic. The rebuild should prefer conservative, editable
  variation structures over pretending to infer every possible substitution perfectly.
- Pescatarian substitutions may not exist in the linked source. The rebuild may create a sensible editable
  placeholder option rather than a source-authored recipe variant.
- Source recipes may use different serving sizes than the household plan. The first pass should use source
  recipe amounts as written and avoid automatic scaling.
- Some current grocery ingredients are household-added sides or serving items not listed in the linked
  recipe. Replacing from source will remove those from generated grocery lists unless they are manually
  added back later.
- Some variations represent household-specific substitutions not present in the source link. Those should
  remain editable but not fabricated.

## Verification

- `npm run build`
- `.venv/bin/python -m pytest -q`
- API spot checks for structured ingredients and grocery amount display.
- Browser checks for Meal Catalog and Grocery + Prep.
- Privacy scan excluding ignored local database and build output.
