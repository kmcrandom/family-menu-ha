# Meal Catalog Screen

## Purpose

The Meal Catalog screen lets the user maintain the meals that suggestions draw from.

## Primary Content

- Active meals.
- Archived meals.
- Likability percentage.
- Prep and cook time.
- Make-ahead score.
- Leftover quality.
- Leftover style.
- Shared ingredients.
- Shared ingredient amounts.
- Meal-level Sunday prep tasks.
- Meal source link and source name.
- Meal cooking instructions.
- Primary or default proteins.
- Diet-compatible alternatives.
- Meal variation dimensions and options.
- Option-level ingredient additions and omissions.
- Option-level ingredient amounts for additions.
- Option-level prep-ahead tasks.
- Simple serving variations.
- Diet compatibility tags.
- Tags.
- Selectable label/tag chips.

## Primary Actions

- Create meal.
- Edit meal.
- Duplicate meal.
- Archive or restore meal.
- Adjust likability.
- Add or edit variation dimensions and options.
- Import starter catalog.
- Export catalog.
- Open source link.
- Select or clear a label/tag filter.

## Editing Requirements

- Likability should be editable as a 0-100 percentage.
- Meal numeric fields such as likability, prep minutes, cook minutes, make-ahead score, and leftover quality should use compact short-field widths on desktop and tablet.
- Meal identity and short metadata fields should share rows where readable, while long text areas such as ingredients, prep tasks, and notes should remain wide.
- The meal list and meal editor should keep a two-column master/detail layout on desktop and tablet where practical.
- The meal list panel should show search first, then the meal list, then label/tag filter chips below the list.
- Variation option rows should keep option name, likability, and archive/restore action on one row on desktop/tablet.
- Option grocery/prep textareas should use compact multi-column layouts on desktop/tablet and collapse cleanly on phone-sized screens.
- Protein alternatives should be easy to edit without duplicating the whole meal.
- Shared ingredients should be visible and editable on the meal.
- Shared ingredient amounts should be visible and editable on the meal without editing JSON.
- Meal-level Sunday prep tasks should be visible and editable on the meal.
- Meal source URL and optional source name should be visible and editable on the meal.
- The source URL editor should include a compact button or icon action beside the URL field to open the link in a new tab when the field has a value.
- Meal instructions should be visible and editable on the meal.
- Instructions should be line-based or otherwise structured enough for the Weekly Plan instructions dialog to show scannable steps.
- Variation dimensions should be easy to add without duplicating the whole meal.
- A dimension can represent primary protein, diet-compatible protein, vegetable mix, sauce, starch/base, pasta shape, prep method, or toppings.
- Each option within a dimension should have its own likability, active/archive state, tags, diet compatibility tags, and optional prep/cook/leftover overrides.
- Each option should expose editable ingredient additions, ingredient omissions, and prep-ahead tasks because selected options directly shape Grocery and Prep.
- Option ingredient additions should include editable amounts and units.
- Grocery-impacting fields should use simple line-based editing so a household can add, remove, or reorder items without writing JSON.
- Ingredient editors may stay line-based if the line format is understandable, but they must support amount, unit, and label. A structured row editor is also acceptable when it remains compact.
- The editor should make it clear which fields affect the generated grocery list and which fields affect Sunday prep.
- The editor should make it clear that source links and instructions affect the Weekly Plan instructions dialog but do not affect recommendations directly.
- Variation dimensions and option editor sections should use the same muted semantic color mapping as Weekly Plan.
- Meal and option compatibility should be editable without requiring code changes when a household adds or removes a dietary profile.
- Instructions should be short and practical, not full recipe essays.
- If instructions are populated from a recipe link, the app should store concise rewritten steps and retain the original source URL for attribution and deeper reference.
- If ingredients and cooking instructions are populated from a meal source link, the app should store them in the local meal catalog only. Source-derived ingredients may replace the meal-level shared ingredient list so the local catalog matches the attached source recipe.
- If cooking instructions are populated from a meal source link, the app should store concise practical steps derived from the source recipe. The app should not store a full copied recipe article.
- A full local source refresh may clear a meal's current ingredients, variations, instructions, timing, and prep tasks while preserving only meal names and source links, then rebuild those fields directly from the attached links.
- A full local source refresh must create a timestamped backup of the ignored local database before clearing or rebuilding data.
- Source-derived protein ingredients should be placed in `variation_primary_protein` option grocery additions. Meal-level shared ingredients should contain the non-protein ingredients common to the recipe.
- If the source-derived default protein is not compatible with a pescatarian profile, the meal should also have a pescatarian protein option. The pescatarian option should be clearly named, tagged as diet-compatible, and use conservative grocery additions that the user can edit later.
- Source-derived variation dimensions should be created for meaningful substitution points, such as protein, sauce, base/starch, vegetable mix, cheese, toppings, or prep method. Variation ingredients should live under the selected option's grocery additions rather than duplicated in shared ingredients.
- Source-derived Sunday prep tasks should include the task, maximum recommended lead time, and storage guidance such as refrigerator, freezer, or airtight container when that can be inferred.
- Source-derived prep time, cook time, total time, make-ahead score, tags, and leftover style should be refreshed from the linked source where possible. Missing fields should use conservative defaults.
- Source-derived ingredient replacement should be conservative about parsing amounts: preserve the recipe ingredient line as a readable label when parsing is unclear, and add amount/unit/category metadata only when the recipe source clearly supports it.
- Source-derived replacement should not fabricate household substitutions or sides that are not present in the linked source recipe. Those can be added manually afterward as meal-level or option-level grocery fields.
- Source-derived ingredient amounts, cooking instructions, source URLs, and household-selected recipe details are private installation data. They should remain in the ignored local database or ignored local seed files and should not be added to tracked generic starter catalog files or specs.
- Archiving a meal removes it from new suggestions but preserves history.
- Archiving a variation option removes that exact option from new suggestions while preserving option history.
- Duplicating a meal should create a new editable meal with a new id.

## Search and Filters

- Search by meal name, ingredient, protein, dietary profile, tag, and leftover style.
- Filter active versus archived.
- Filter by slow cooker, fast weeknight, simple-serving-friendly, vegetarian, vegan, pescatarian, freezer-friendly, or other tags.
- Show available meal tags or labels as compact selectable chips below the meal list, not above it.
- Selecting a tag/label filters the meal list to meals with that tag while keeping text search usable.
- Selected tag/label filters should be clearly visible and easy to clear.

## Acceptance Criteria

- A user can change a meal's likability and see it affect future scoring.
- A user can add a diet-compatible protein alternative to an existing shared-base meal.
- A user can add a new variation dimension or option under an existing meal and later see it in the Weekly Plan screen.
- A user can change a variation option's likability and see it affect future option scoring.
- A user can edit shared meal ingredients and see those changes reflected in Grocery and Prep for weeks containing that meal.
- A user can edit shared meal ingredient amounts and see those amounts reflected in Grocery and Prep for weeks containing that meal.
- A locally enriched meal source can replace the meal's shared grocery ingredient list from the source recipe without requiring the user to edit JSON, and those ingredients and amounts appear in the Meal Catalog editor.
- A locally enriched meal source can refresh the meal's cooking instructions from the source recipe without requiring the user to edit JSON, and those steps appear in the Meal Catalog editor and Weekly Plan instructions dialog.
- A full local source refresh backs up the current local database before clearing and rebuilding source-derived meal fields.
- After a full local source refresh, meal-level shared ingredients exclude protein-specific ingredients when those ingredients belong to protein variations.
- After a full local source refresh, a meal with a non-pescatarian source protein has both a default protein option and a pescatarian-compatible option.
- After a full local source refresh, source-derived substitution points appear as variation dimensions/options with grocery-impacting ingredients stored on the options.
- After a full local source refresh, Sunday prep tasks include lead-time and storage guidance when available.
- After a full local source refresh, prep and cook time fields are updated from source data where available.
- A user can edit meal-level prep-ahead tasks and see those changes reflected in Sunday Prep for weeks containing that meal.
- A user can edit a meal source URL and see that link on both Meal Catalog and Weekly Plan.
- A user can open the currently selected meal's source URL directly from the source URL field area.
- A user can edit meal cooking instructions and open them from Weekly Plan.
- A user can edit variation-option ingredient additions and prep-ahead tasks and see those changes reflected when that option is selected in a weekly plan.
- A user can edit variation-option ingredient amounts and see those amounts reflected when that option is selected in a weekly plan.
- Locally enriched variation-option ingredient amounts appear in the option editor and affect Grocery and Prep when that option is selected.
- Variation dimensions use consistent muted colors that match Weekly Plan for the same dimension key.
- A user can edit meal and option diet tags so common-compatible mode can filter suggestions correctly.
- A user can archive a meal without breaking old weekly plans or history.
- A user can find all high-likability meals quickly.
- A user can select a visible meal tag/label and filter the meal list by that selection.
- Meal Catalog labels appear below the meal list.
- Meal Catalog remains compact enough on desktop and tablet that editing common meal metadata does not require scrolling through a long single-column form.
