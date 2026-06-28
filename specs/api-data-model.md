# API and Data Model

## Principles

- Store structured meal data so the UI can edit it without code changes.
- Store meal events separately from weekly plans so history remains valid if a plan changes later.
- Track meal and variation-option usage separately: a meal can be familiar while a specific protein, sauce, pasta, vegetable set, or base is underused.
- Preserve manual user choices and locked meals during regeneration.
- Keep the initial schema small, but leave room for variations, tags, grocery grouping, and prep tasks.

## Entities

### Meal

Represents a dinner concept such as a build-your-own bowl, pasta dish, soup, sheet-pan meal, sandwich, or other user-defined dinner.

Fields:

- `id`: stable slug.
- `name`: display name.
- `status`: `active` or `archived`.
- `likability`: integer 0-100. Higher values make a meal eligible more often over time.
- `active_prep_minutes`: estimated hands-on prep.
- `cook_minutes`: elapsed cooking time.
- `make_ahead_score`: integer 0-100.
- `leftover_quality`: integer 0-100.
- `leftover_style`: category such as `bowl`, `pasta`, `sandwich`, `pizza`, `soup`, `sheet_pan`, `handheld`, or `mixed`.
- `tags`: searchable tags.
- `diet_tags`: dietary compatibility tags such as `vegetarian`, `vegan`, `pescatarian`, `contains_meat`, `contains_pork`, `contains_beef`, `contains_shellfish`, `contains_dairy`, or custom tags.
- `shared_ingredients`: ingredients used by most versions. Each item should support label and amount metadata.
- `primary_proteins`: unrestricted or default proteins for households that use separate protein variations.
- `alternate_proteins`: diet-specific or preference-specific alternatives for households that use separate variation mode.
- `prep_ahead`: tasks that can be done before the meal day.
- `instructions`: short cooking instructions.
- `source_url`: optional recipe or reference link for the meal.
- `source_name`: optional readable source label derived from the link or entered manually.
- `simple_serving_variations`: simplified serving options for household members who prefer lower-risk variants.
- `notes`: optional free text.
- `created_at`, `updated_at`.

Recipe links and instructions are private catalog data:

- Starter or tracked repo data should not include a household's specific selected recipe links or instructions unless they are generic examples.
- The local database may store meal-specific links and instructions for the household installation.
- Instructions populated from recipe links should be concise, practical summaries written for the app, not copied long-form recipe text.
- Source URLs should be preserved so the user can open the original recipe when they need full details, timing nuance, photos, or attribution.
- A local source refresh may intentionally reset a meal to source-derived data. In that flow the app should preserve only stable meal identity, name, source URL, and source name before rebuilding ingredients, instructions, timing, prep tasks, variation dimensions, and variation options from the linked source.
- Source-refresh tooling must create a timestamped backup of the ignored local database before clearing or rebuilding source-derived fields.
- Source-derived protein ingredients should live under protein variation option `ingredient_additions`, not meal-level `shared_ingredients`, so choosing a different protein variation naturally removes the unselected protein from the grocery list.
- When a linked source recipe contains a non-pescatarian default protein, the source refresh should create a diet-compatible pescatarian protein variation option where practical, even if the source does not provide one. Its ingredient additions should be conservative and editable.
- Source-derived substitute-able ingredients, such as proteins, sauces, bases, vegetables, cheeses, or toppings, may become variation dimensions/options when the source clearly presents alternatives or when the ingredient is a natural substitution point.
- Source-derived prep-ahead tasks should include storage guidance and maximum recommended lead time when it can be inferred from the source or common food-safety practice.

### Meal Variation Dimension

Represents one independent way a meal can vary. Examples:

- `variation_primary_protein`: default or unrestricted protein options.
- `variation_diet_protein`: protein options compatible with one or more configured dietary profiles.
- `variation_starch_or_base`: rice, pasta, bread, greens, or another base.
- `variation_sauce`: sauce or seasoning options.
- `variation_vegetables`: vegetable combinations.

Fields:

- `id`.
- `meal_id`.
- `name`.
- `key`: stable semantic key such as `variation_primary_protein`, `variation_diet_protein`, `variation_starch_or_base`, `variation_sauce`, `variation_vegetables`, `variation_base`, `variation_prep_method`, or `variation_toppings`.
- `selection_mode`: initially `single`; future-compatible with `multi`.
- `required`: whether a weekly plan should select an option from this dimension.
- `color`: optional user-selected color token or custom color value used to visually identify this dimension across Meal Catalog and Weekly Plan. Existing dimensions without a stored color should continue to receive the stable semantic fallback color derived from `key`.
- `display_order`.
- `status`: `active` or `archived`.

Variation dimensions should support reuse and user-defined types:

- Existing dimension keys and names used anywhere in the catalog should be available as reusable variation type suggestions when adding a dimension to another meal.
- Reusable suggestions should include common built-in concepts such as primary protein, diet-compatible or pescatarian protein, vegetables, sauce, starch/base, toppings, and prep method when those concepts exist in the catalog or starter defaults.
- A meal should not offer reusable variation type suggestions for active dimensions it already has.
- Custom variation types should store a stable generated `key`, a display `name`, and an optional color.
- Removing a variation dimension from a meal should archive it by default rather than hard-deleting it, so existing weekly plans and history remain understandable. A future destructive delete may exist only behind explicit confirmation and should not be the default.
- Archived variation dimensions should be omitted from new recommendations and ordinary add-type suggestion filtering, but remain available for historical plans and restore flows.

### Meal Variation Option

Represents one selectable value within a variation dimension.

Fields:

- `id`.
- `dimension_id`.
- `meal_id`.
- `name`.
- `status`: `active` or `archived`.
- `likability`: integer 0-100. Higher values make this option eligible more often within its dimension.
- `value`: optional structured value, such as a protein name, sauce name, pasta shape, or list of vegetables.
- `diet_tags`: dietary compatibility tags for filtering options in common-compatible mode.
- `compatible_diet_profiles`: optional list of dietary profile ids this option can satisfy in separate-variation mode.
- `ingredient_additions`: ingredients added by this option. Each item should support label and amount metadata.
- `ingredient_omissions`: meal-level shared ingredients omitted when this option is selected. Matching is label-based after trimming and case-normalization.
- `prep_ahead`: option-specific prep tasks.
- `instructions`: option-specific cooking notes.
- `tags`: option-level tags.
- `active_prep_minutes_override`: optional override.
- `cook_minutes_override`: optional override.
- `make_ahead_score_override`: optional override.
- `leftover_quality_override`: optional override.
- `leftover_style_override`: optional override.
- `created_at`, `updated_at`.

The meal-level fields describe the broad dinner format. Variation dimensions describe the independent knobs for that meal. Variation options describe the exact selected values used for a week and for history tracking. A concrete planned dinner is the parent meal plus a set of selected option IDs, not a pre-baked cartesian-product variation.

When Grocery and Prep is generated, option `ingredient_omissions` remove matching labels from that planned meal's `shared_ingredients` contribution before option additions are applied. Omissions do not remove ingredients contributed by other planned meals or by option `ingredient_additions`.

Protein-specific groceries should be modeled as selected option additions rather than meal-level shared ingredients. This avoids needing broad omissions for every alternate protein and keeps grocery output aligned with the selected variation.

### Ingredient Item

Represents one recipe or grocery ingredient.

Fields:

- `label`: ingredient name, such as `rice`, `bell peppers`, or `soy sauce`.
- `amount`: optional numeric or text amount, such as `2`, `1.5`, `1/2`, `1 1/2`, `one bunch`, or `to taste`.
- `unit`: optional unit, such as `cups`, `lb`, `oz`, `tbsp`, `cloves`, `cans`, or `each`.
- `category`: optional grocery grouping override.
- `note`: optional preparation or buying note, such as `thinly sliced` or `low sodium`.

Ingredient fields that previously accepted `list[str]` should be backward-compatible:

- Existing string ingredients should be interpreted as ingredient items with `label` set to the string and blank amount/unit/note/category.
- API responses should prefer the structured item shape after migration, while import code may accept either strings or structured ingredient items.
- Matching for ingredient omissions remains based on `label`, not amount or unit.

Grocery aggregation should carry amount information into generated grocery rows:

- If identical ingredient labels have compatible amount/unit pairs, the app should sum the amounts.
- Compatible weight units include pounds, ounces, and grams, including common abbreviations such as `lb`, `lbs`, `oz`, `g`, and `grams`.
- Compatible volume units include milliliters, liters, teaspoons, tablespoons, and cups, including common abbreviations such as `ml`, `mL`, `L`, `tsp`, `tbsp`, `cup`, and `cups`.
- Fractional and mixed-number numeric amounts such as `1/2 cup`, `1 1/2 cups`, and `0.5 cup` should be parsed for summing.
- Simple count amounts such as `5 carrots` should be represented as an amount with no unit or an `each`-style unit, and should be summed with other count amounts for the same ingredient label.
- If amounts cannot be safely summed, the app should preserve readable per-source amount text rather than dropping the amount.
- Ingredients without amounts should still appear normally.

### Household Member

Represents a person or recurring eater for meal planning. It should not assume fixed household relationships.

Fields:

- `id`.
- `display_name`.
- `status`: `active` or `archived`.
- `dinner_servings`: decimal or integer serving count.
- `leftover_lunch_servings`: decimal or integer serving count.
- `dietary_profile_ids`: list of dietary profiles assigned to this member.
- `preference_tags`: optional planning hints such as `simple_servings`, `spicy_ok`, or custom tags.
- `created_at`, `updated_at`.

### Dietary Profile

Represents a reusable dietary pattern or restriction.

Fields:

- `id`.
- `name`.
- `type`: `omnivore`, `vegetarian`, `vegan`, `pescatarian`, `no_pork`, `no_beef`, or `custom`.
- `excluded_tags`: diet tags that should be filtered out.
- `included_tags`: diet tags that are explicitly acceptable or preferred.
- `notes`.
- `created_at`, `updated_at`.

### Weekly Plan

Represents the selected dinners for one Sunday-starting planning week.

Fields:

- `id`.
- `week_start_date`.
- `shopping_date`.
- `target_dinner_count`, initially 5.
- `status`: `draft`, `planned`, `completed`, or `archived`.
- `notes`.
- `created_at`, `updated_at`.

### Vacation Block

Represents a day or full week where the household should not plan dinner in the app.

Fields:

- `id`.
- `weekly_plan_id`.
- `start_date`.
- `end_date`.
- `scope`: `day` or `week`.
- `label`, defaulting to `Vacation`.
- `created_at`, `updated_at`.

Rules:

- A weekly plan can have multiple vacation blocks.
- A full-week vacation block covers the plan's whole Sunday-starting week.
- A day vacation block covers one calendar date.
- Vacation blocks are private local data and should not be part of tracked starter data.
- Creating or updating a vacation block must delete planned meals whose `planned_date` falls inside the block.
- Removing a vacation block must not automatically regenerate meals; the user can generate/regenerate explicitly.

### Planned Meal

Represents one meal slot in a weekly plan.

Fields:

- `id`.
- `weekly_plan_id`.
- `meal_id`.
- `variation_selections`: map of variation dimension id to selected option id.
- `diet_group_selections`: optional map of dietary profile id to variation option ids when separate-variation mode is enabled.
- `planned_date`.
- `position`.
- `meal_slot`, initially `dinner`.
- `servings_dinner`, initially 4.
- `leftover_lunch_servings`, initially 2.
- `locked`: whether regeneration must preserve this row.
- `variation_locks`: optional map of variation dimension id to boolean, allowing sauce to be locked while protein remains swappable, for example.
- `state`: `planned`, `eaten`, `skipped`, or `moved`.
- `notes`.
- `created_at`, `updated_at`.

### Meal Event

Represents what actually happened and powers history.

Fields:

- `id`.
- `meal_id`.
- `planned_meal_id`, optional.
- `eaten_date`.
- `variation_selections`: map of variation dimension id to selected option id at the time the meal was eaten.
- `servings_dinner`.
- `leftover_lunch_servings`.
- `feedback`: optional `liked`, `neutral`, or `disliked`.
- `notes`.
- `created_at`.

### Checklist Item

Represents persisted checked state for generated grocery and prep rows in a weekly plan.

Fields:

- `id`: deterministic id from weekly plan, item kind, and label.
- `weekly_plan_id`.
- `kind`: `grocery` or `prep`.
- `label`.
- `category`.
- `source`.
- `checked`.
- `custom`: reserved for future manually-added rows.
- `position`.
- `created_at`, `updated_at`.

### Household Preferences

Fields:

- `household_members`.
- `dietary_profiles`.
- `mixed_diet_mode`: `separate_variations` or `common_compatible_only`.
- `week_start_day`, initially Sunday.
- `shopping_day`, initially Sunday.
- `default_week_size`, initially 5.
- `default_dinner_servings`, initially 4.
- `default_leftover_lunch_servings`, initially 2.
- `max_same_meal_per_week`, initially 1.
- `soft_repeat_gap_days`.
- `avoid_consecutive_leftover_styles`.
- `recommendation_weights`.
- `variation_recency_weight`.
- `variation_frequency_weight`.

## Recommendation and History Granularity

The app should track both:

- Meal-level usage, such as a user-defined dinner was eaten on a date.
- Variation-option usage, such as a selected default protein, diet-compatible protein, sauce, base, vegetable set, or prep method was eaten on a date.

The recommendation engine should first avoid overusing the same top-level meal, then prefer underused or high-likability options within each selected meal's variation dimensions. A frequent meal can still be suggested when its likability is high, but the app should nudge toward less-used options when that improves variety.

In the Weekly Plan UI, top-level meal actions and variation actions are separate:

- Replacing a meal swaps one dinner concept for another.
- Reordering moves a dinner to another day without changing selected variation options.
- Swapping a primary-protein option keeps the meal but changes the default protein.
- Swapping a diet-protein option keeps the meal but changes the compatible alternative.
- Swapping a sauce, base, or vegetable option keeps the meal and changes only that dimension.

When `mixed_diet_mode` is `separate_variations`, the recommendation engine may choose different compatible options for different diet profiles within the same shared-base meal. When it is `common_compatible_only`, the engine must exclude any meal or option that conflicts with any active household member's dietary profile.

Historical reporting should show "last eaten meal" and "last used option" per variation dimension where possible.

## Target V1 API Surface

Read and edit meal catalog:

- `GET /api/v1/meals`
- `GET /api/v1/meals/{meal_id}`
- `PATCH /api/v1/meals/{meal_id}`
- `POST /api/v1/meals/{meal_id}/archive`
- `POST /api/v1/meals/{meal_id}/restore`
- `GET /api/v1/meals/{meal_id}/variation-dimensions`
- `POST /api/v1/meals/{meal_id}/variation-dimensions`
- `PATCH /api/v1/variation-dimensions/{dimension_id}`
- `POST /api/v1/variation-dimensions/{dimension_id}/archive`
- `POST /api/v1/variation-dimensions/{dimension_id}/restore`
- `POST /api/v1/variation-dimensions/{dimension_id}/options`
- `PATCH /api/v1/variation-options/{option_id}`
- `POST /api/v1/variation-options/{option_id}/archive`
- `POST /api/v1/variation-options/{option_id}/restore`

Weekly planning:

- `GET /api/v1/plans/current`
- `GET /api/v1/plans?week_start_date=YYYY-MM-DD`
- `POST /api/v1/plans`
- `POST /api/v1/plans/{plan_id}/generate`
- `POST /api/v1/plans/{plan_id}/vacation-blocks`
- `PATCH /api/v1/vacation-blocks/{block_id}`
- `DELETE /api/v1/vacation-blocks/{block_id}`
- `PATCH /api/v1/planned-meals/{planned_meal_id}`
- `POST /api/v1/planned-meals/{planned_meal_id}/mark-eaten`
- `POST /api/v1/planned-meals/{planned_meal_id}/skip`

Supporting views:

- `GET /api/v1/household`
- `PATCH /api/v1/household`
- `POST /api/v1/household/members`
- `PATCH /api/v1/household/members/{member_id}`
- `POST /api/v1/household/dietary-profiles`
- `PATCH /api/v1/household/dietary-profiles/{profile_id}`
- `GET /api/v1/plans/{plan_id}/grocery-prep`
- `PATCH /api/v1/plans/{plan_id}/checklist-items`
- `GET /api/v1/history`
- `POST /api/v1/history`
- `DELETE /api/v1/history/{event_id}`
- `GET /api/v1/preferences`
- `PATCH /api/v1/preferences`
- `GET /api/v1/export`

Deferred API surface:

- Create new top-level meals directly in the UI.
- Add custom grocery or prep checklist rows.
- Import/merge backup JSON with explicit overwrite behavior.
- Public account or cloud sync.
- Automated recipe-link lookup as a hosted service. Recipe lookup may be done by local tooling for a private installation, but discovered household links and generated instructions should remain in the local database or ignored local files.

## API Response Requirements

- Recommendation responses should include selected meals plus reason codes.
- Validation errors should identify the field and the constraint.
- APIs should not require authentication for local development.
- A future Home Assistant add-on can rely on ingress or an admin token if remote exposure is added.
- API responses should not leak private seed-file paths except in local settings/admin views.

## Migration Expectations

- SQLite schema migrations should be explicit and testable.
- Seed import should be idempotent by meal `id`.
- User-edited meals should not be overwritten by a future seed update unless an import explicitly requests it.
- Migrations should preserve existing local meal catalogs, planned meals, history, and checklist state when adding household member and dietary profile tables.
