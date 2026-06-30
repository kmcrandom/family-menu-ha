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
- Label/tag filtering opened from the search area.

## Primary Actions

- Create meal.
- Save newly created meal.
- Enter edit mode for the selected meal.
- Save meal edits.
- Duplicate meal.
- Archive or restore meal.
- Adjust likability.
- Add or edit variation dimensions and options.
- Add or remove variation dimensions while editing.
- Import starter catalog.
- Export catalog.
- Open source link.
- Cancel meal edits.
- Open label/tag filters from the search area.
- Select or clear label/tag filters.

## Editing Requirements

- Selecting an existing meal should open the Meal Catalog detail in read-only view mode by default.
- Read-only view mode should show the selected meal's details, grocery-impacting fields, Sunday prep tasks, source link, instructions, variation dimensions, and variation options without allowing accidental field edits.
- Read-only view mode should provide a clear top action area with Archive or Restore and Edit actions.
- Archive or Restore should be available while not editing and hidden while editing.
- Archiving a meal should require a popup confirmation before the archive action is sent.
- Restoring an archived meal does not require confirmation.
- Edit mode should expose the existing meal editing controls and replace the read-only actions with Save and Cancel in the same top action area.
- Save should persist meal edits from the top action area.
- Cancel should exit edit mode and restore the form to the selected meal's saved values without saving.
- Switching to a different existing meal should return the detail pane to read-only view mode for that meal.
- Creating a meal should be available from the Meal Catalog screen without requiring seed-file edits, direct database edits, import/export, or developer tools.
- The create action should start an editable new-meal draft with the same fields used for editing existing meals, including name, likability, timing, source, labels, shared grocery ingredients, prep tasks, instructions, and notes.
- A new-meal draft should use neutral defaults that match existing meal editing defaults where practical: active status, likability 80, active prep 20 minutes, cook time 20 minutes, make-ahead 50, leftover quality 70, leftover style `mixed`, and empty optional lists/text fields.
- Saving a new-meal draft should create a persisted active meal, assign a stable unique id derived from the meal name or an equivalent backend slug strategy, select the saved meal, and return the detail pane to read-only view mode.
- The user should not need to enter a slug or id manually when creating a meal.
- The meal name is required for saving a new meal. Empty or whitespace-only names should keep the user in edit mode and show a clear validation or save error without creating a blank meal.
- If the generated meal id would collide with an existing meal, the backend should create a unique stable id rather than overwriting the existing meal.
- Canceling a new-meal draft should discard the unsaved draft and return to the previously selected meal when one exists, otherwise to the empty/no-selection state.
- New meals should appear in Meal Catalog search and label/tag filtering immediately after save.
- New meals should be eligible for Weekly Plan suggestions and replacement selectors after save, subject to active status and compatibility filtering.
- Newly created meals may start with no variation dimensions; the user can add variations after the meal has been created and selected.
- Creating a meal or duplicating a meal should open the resulting meal in edit mode so the user can immediately fill in or adjust fields.
- If the user has unsaved edits and attempts to leave edit mode or select another meal, the app should either preserve the local draft until saved or clearly confirm discarding changes.
- Likability should be editable as a 0-100 percentage.
- Meal numeric fields such as likability, prep minutes, cook minutes, make-ahead score, and leftover quality should use compact short-field widths on desktop and tablet.
- Meal identity and short metadata fields should share rows where readable, while long text areas such as ingredients, prep tasks, and notes should remain wide.
- The meal list and meal editor should keep a two-column master/detail layout on desktop and tablet where practical.
- The meal list panel should show search first, with a compact label/tag filter icon in the search area.
- The meal list panel should not show a persistent label/tag chip section below the list, because that consumes too much vertical space on phone-sized screens.
- The meal list card should align near the top of the catalog layout and, on wider screens, should start in line with the meal editor card rather than leaving excessive empty space above it.
- Variation option rows should keep option name, likability, and archive/restore action on one row on desktop/tablet.
- Option grocery/prep textareas should use compact multi-column layouts on desktop/tablet and collapse cleanly on phone-sized screens.
- Protein alternatives should be easy to edit without duplicating the whole meal.
- Shared ingredients should be visible and editable on the meal.
- Shared ingredient amounts should be visible and editable on the meal without editing JSON.
- Meal-level Sunday prep tasks should be visible and editable on the meal.
- Meal source URL and optional source name should be visible and editable on the meal.
- The selected meal header should include the source-link open action when a source URL exists.
- The source URL editor should not include a second open-source icon beside the URL field because the same action is already available in the selected meal header.
- Meal instructions should be visible and editable on the meal.
- Instructions should be line-based or otherwise structured enough for the Weekly Plan instructions dialog to show scannable steps.
- Variation dimensions should be easy to add and remove while editing without duplicating the whole meal.
- The add variation entry point should display under the selected meal's current active variation dimensions, not above them.
- The variation type, custom name/key, and color controls for adding a variation should not be visible by default. An Add variation button should reveal those controls in an expanded panel or popup.
- Adding a variation dimension while editing should show reusable variation types that have been used before in the catalog, such as primary protein, pescatarian or diet-compatible protein, vegetables, sauce, starch/base, toppings, or prep method, only after the user activates Add variation.
- Reusable variation type suggestions should filter out active variation dimensions already present on the selected meal.
- Adding a variation dimension should also offer a custom variation type path where the user can enter a new display name, generate or edit a stable key, and choose a color.
- Removing a variation dimension from a meal should archive that dimension by default and remove it from new recommendations while preserving historical plans and usage. The UI should use clear remove/archive language and confirmation when removal affects existing options.
- A dimension can represent primary protein, diet-compatible protein, vegetable mix, sauce, starch/base, pasta shape, prep method, or toppings.
- Variation dimensions should show their current color accent while editing, but the color palette should not be visible inline on existing variation rows by default.
- Existing variation dimensions should provide a compact icon button with a color dropper icon. Activating it should open a popup for selecting a different color.
- Variation color selection should show a preset palette of Material Design colors suitable for the app's muted dark UI.
- Preset color choices already used by active variation dimensions on the selected meal should be filtered out or disabled.
- The color selector should also include a custom color picker for households that need a color outside the preset palette.
- Custom colors should remain readable in dark mode and should not be the only cue for identifying a variation dimension.
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
- Show a compact filter icon in or beside the search bar when label/tag filters are available.
- Opening the filter control should reveal the available meal tags or labels in a phone-friendly selection UI.
- The label/tag selection UI should allow selecting and clearing labels without requiring horizontal scrolling.
- Selecting a tag/label filters the meal list to meals with that tag while keeping text search usable.
- Selected tag/label filters should be clearly visible from the search/filter area and easy to clear.

## Acceptance Criteria

- A user can choose Create meal from Meal Catalog and receive an editable new-meal draft.
- A user can save a new meal with at least a name and see it selected in read-only mode afterward.
- Saving a new meal without a non-empty name does not create a meal and communicates the problem.
- A newly saved meal appears in the catalog list, can be found by search, and can be filtered by any labels entered during creation.
- A newly saved active meal is returned by the meals API and can be selected as a replacement meal in Weekly Plan without reloading the whole app.
- Canceling a new-meal draft does not create a meal and restores the previous catalog selection when available.
- Selecting an existing meal opens the detail pane in read-only mode by default.
- The selected meal cannot be changed until the user activates the Edit action.
- Activating Edit switches the selected meal detail into editable controls without changing the selected meal.
- Read-only mode shows Archive or Restore and Edit actions in the selected meal header.
- Activating Archive from read-only mode opens a confirmation popup before archiving the selected meal.
- Edit mode shows Save and Cancel actions in the selected meal header, and hides Archive or Restore.
- Canceling edit mode discards unsaved form changes and returns to read-only mode for the selected meal.
- Selecting another existing meal exits edit mode and shows the newly selected meal read-only, unless unsaved edits require a discard/preserve flow.
- Creating or duplicating a meal opens the new meal in edit mode.
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
- A user can open the currently selected meal's source URL directly from the selected meal header.
- The Source URL form field does not show a duplicate open-source icon button.
- A user can edit meal cooking instructions and open them from Weekly Plan.
- A user can edit variation-option ingredient additions and prep-ahead tasks and see those changes reflected when that option is selected in a weekly plan.
- A user can edit variation-option ingredient amounts and see those amounts reflected when that option is selected in a weekly plan.
- Locally enriched variation-option ingredient amounts appear in the option editor and affect Grocery and Prep when that option is selected.
- Variation dimensions use consistent muted colors that match Weekly Plan for the same dimension key.
- A user can add an existing reusable variation type to a meal while editing, and the list excludes variation types already active on that meal.
- A user can add a brand new variation type with a chosen preset Material Design color or a custom color.
- The Add variation button appears under the current active variation dimensions and keeps variation type, name/key, and color controls hidden until activated.
- Existing variation dimensions do not show inline color palettes while editing; the color dropper icon opens color selection in a popup.
- Color choices already used by active variation dimensions on the selected meal are not offered as duplicate preset choices.
- A user can remove a variation dimension from a meal while editing, and it no longer appears for new planning suggestions while historical data remains intact.
- A user can edit meal and option diet tags so common-compatible mode can filter suggestions correctly.
- A user can archive a meal without breaking old weekly plans or history.
- A user can find all high-likability meals quickly.
- A user can open label/tag filters from the search area, select a label, and filter the meal list by that selection.
- A user can clear the selected label/tag filter from the search/filter area.
- Meal Catalog labels do not appear as a persistent chip section below the meal list.
- On phone-sized screens, label/tag filtering remains usable without the filter list being cut off.
- On wider screens, the meal list card starts in line with the meal editor card.
- Meal Catalog remains compact enough on desktop and tablet that editing common meal metadata does not require scrolling through a long single-column form.
