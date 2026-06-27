# Grocery and Prep Screen

## Purpose

The Grocery and Prep screen turns the selected weekly plan into a Sunday shopping and prep checklist.

By default, this screen should open to the next upcoming Sunday planning week, not necessarily the
current calendar week's Sunday. This keeps the grocery workflow pointed at the next shopping trip.
For example, on any day from Monday through Saturday, the default Grocery and Prep week is the
following Sunday. On Sunday, the default Grocery and Prep week is that same day.

After the user changes the Grocery and Prep week, the screen should remember that viewed week for
the current browser session. If the user navigates to another app screen and later returns to
Grocery and Prep, it should reopen to its own last viewed Grocery and Prep week rather than resetting
to the default next-shopping week. This remembered Grocery and Prep week must be independent from
the remembered Weekly Plan week, so browsing one page does not change the other page's selected week.

## Primary Content

- Week summary.
- Previous/current/next week controls matching the Weekly Plan screen.
- Last viewed Grocery and Prep week for the current browser session.
- Compact week metadata and week navigation arranged together on desktop and tablet.
- Grocery list grouped by area or type.
- Shared ingredients.
- Ingredient amounts and units where available.
- Primary protein ingredients.
- Diet-compatible protein ingredients.
- Pantry/common items.
- Sunday prep tasks.
- Weekday quick tasks.

## Primary Actions

- Check off grocery items.
- Check off prep tasks.
- Move to the previous week.
- Return to the current planning week.
- Move to the next week.

Deferred actions:

- Add custom grocery item.
- Add custom prep task.
- Hide pantry items for the current week.
- Print or export the list from this screen.

## Grocery Aggregation Requirements

- Grocery output should show ingredient amounts and units when the meal catalog provides them.
- Grocery output should use locally enriched source-derived ingredient lists and amounts when those have been saved into the meal catalog.
- Ingredients should retain source meals so the user can understand why each item appears.
- Ingredient amount display should retain source context when multiple meals or options contribute the same label.
- Protein-specific ingredients should show which eater group or variation needs them.
- Variation-option-specific ingredients should show the selected option, variation dimension, and parent meal.
- Protein ingredients from source-refreshed meals should appear only for the selected protein variation, because those ingredients are stored as option grocery additions.
- Duplicate ingredient names should merge when safe.
- Duplicate ingredient amounts should be summed when the app can safely combine compatible numeric amounts in the same unit family.
- Weight amounts should sum across pounds, ounces, and grams.
- Volume amounts should sum across milliliters, liters, teaspoons, tablespoons, and cups.
- Count amounts such as `5 carrots` should sum when the ingredient label matches and no incompatible unit is present.
- If duplicate ingredient amounts cannot be safely summed, the grocery list should show readable per-source amounts rather than hiding or guessing.
- Selected variation options can omit meal-level shared ingredients. Omitted ingredients should not appear in the generated grocery list for that planned meal when the omitted label matches a shared ingredient label after trimming and case-normalization.
- If the same ingredient is needed by another planned meal or by another selected option, it should remain in the grocery list with the remaining source context.

## Prep Requirements

- Sunday prep should prioritize tasks that reduce weekday active prep.
- Slow cooker freezer bags, chopped vegetables, cooked rice, sauces, and portioned toppings should be visible.
- Tasks should be grouped into Sunday prep and weekday finishing tasks.

## Acceptance Criteria

- A generated weekly plan produces a grocery list.
- A generated grocery list displays ingredient amounts and units from meal-level shared ingredients and selected option additions.
- A generated grocery list reflects locally enriched source-derived ingredient lists and amounts from the meal catalog without needing any tracked private recipe data.
- A generated weekly plan produces a Sunday prep checklist.
- Grocery and Prep opens by default to the next upcoming Sunday planning week.
- Grocery and Prep remembers its last viewed week during the current browser session after the user changes weeks.
- Grocery and Prep's remembered week is independent from Weekly Plan's remembered week.
- Grocery and Prep uses the same compact previous/current/next week navigation model as Weekly Plan.
- Changing weeks reloads grocery and prep checklist state for the selected weekly plan without generating meals.
- Checked items persist separately for each selected weekly plan.
- Variation-option ingredient omissions remove matching meal-level shared ingredients from the generated grocery list for that planned meal.
- Ingredient omissions do not remove ingredients contributed by other meals or by selected option additions.
- Changing a source-refreshed protein variation changes the protein-specific groceries by removing the previously selected option's additions and adding the newly selected option's additions.
- Duplicate grocery items with compatible weight, volume, or count amounts show a summed amount.
- Duplicate grocery items with incompatible, missing, or text amounts preserve per-source amount details.
- Grocery and Prep keeps grocery and prep columns side by side on desktop/tablet and collapses to a single column on phone-sized screens.
- Checklist rows remain readable while using compact spacing and avoiding excessive vertical padding.

Deferred acceptance criteria:

- The user can add manual grocery items without editing the meal catalog.
