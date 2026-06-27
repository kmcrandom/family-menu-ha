# Starter Meal Catalog

## Purpose

The starter catalog gives a new installation enough generic data to understand the app without exposing any specific household's real diet, favorite meals, likability scores, meal history, or weekly plan choices. The catalog should be imported as editable data, not treated as hardcoded behavior.

## Privacy Requirements

- Public git-tracked seed data must be generic and reusable by any household.
- Public seed data must not mention a specific relationship label, family member, household size, or private dietary arrangement.
- Public seed data must not include the installing user's real selected meal list, likability ratings, grocery habits, prep notes, or eating history.
- User-specific catalogs should live in ignored local files, such as `data/local-starter-meal-catalog.json`, or in the ignored SQLite database.
- The app may ship a small generic example catalog, but it should be clearly labeled as sample data.
- A user's real catalog should be created through the UI, imported from a private local file, or preserved in the local database.

## Public Generic Starter Data

If the repository includes tracked seed data, it should be generic and minimal. Suggested examples should be broad meal templates rather than a household's real menu:

- Build-your-own bowl.
- Pasta or noodle dinner.
- Soup or stew.
- Sheet-pan dinner.
- Sandwich or wrap night.
- Slow-cooker shared-base meal.
- Breakfast-for-dinner or simple pantry meal.

The public sample catalog should demonstrate variation dimensions, prep-ahead tasks, and grocery aggregation without implying the installer's real household preferences.

Private installation data should not be captured in `specs/starter-meal-catalog.json` or `data/starter-meal-catalog.json` if those files are tracked by git. During implementation, either:

- Replace tracked `starter-meal-catalog.json` files with generic sample data, or
- Rename tracked examples to `*.example.json` and ignore the real `starter-meal-catalog.json`.

For the current local installation, the existing selected meals should be preserved by keeping the local SQLite database and/or a private seed file outside tracked git files.

## Required Fields Per Meal

Each meal should have:

- Stable `id`.
- Display `name`.
- `likability` from 0-100.
- Prep and cook time estimates.
- Make-ahead and leftover quality scores.
- Leftover style.
- Tags.
- Shared ingredients.
- Shared ingredient amounts where useful.
- Primary or default proteins where applicable.
- Diet-compatible alternatives where applicable.
- Meal variation dimensions and options with option-level likability.
- Option-level ingredient additions with amounts where useful.
- Prep-ahead tasks.
- Short instructions.
- Optional generic source URL and source name.
- Simple serving variations.

## Generic Likability Guidance

- Public starter data should use neutral, non-personal default likability values.
- Real household likability ratings should be edited locally and persisted in the ignored database.
- Public examples should avoid implying that any specific meal is favored by the installing household.

## Generic Variation Guidance

Starter variation data should be decomposed into independent dimensions rather than pre-baked combinations. Examples:

- Protein or main component: `variation_primary_protein` or `variation_diet_protein`.
- Base or starch: `variation_starch_or_base`.
- Sauce or seasoning: `variation_sauce`.
- Vegetable set: `variation_vegetables`.
- Prep method: `variation_prep_method`.

The app should track how often each option is used separately from the parent meal and separately from other dimensions. For example, a meal template may be frequent while one sauce, base, or diet-compatible protein option remains underused.

## Seed Import Rules

- Import should be idempotent by meal id.
- Import should accept legacy string ingredients and structured ingredient objects with label/amount/unit/note/category.
- Import may accept `source_url`, `source_name`, and `instructions` for generic examples.
- Existing user edits should be preserved by default.
- A future seed update may add new meals or missing fields, but should not overwrite user-specific likability or notes without confirmation.
- Household-specific recipe links and generated instructions should stay in ignored private seed files or the local database.
- Household-specific source-derived ingredient amounts should stay in ignored private seed files or the local database. Tracked starter examples may demonstrate the ingredient amount format, but they should not include a household's chosen recipe details.
- Private seed paths should be gitignored.
- The default local SQLite database should be gitignored.
- Exported backups should be treated as private unless the user explicitly chooses to publish sanitized sample data.
