# Product Requirements

## Problem

Weekly dinner planning for a household gets repetitive and mentally expensive. Different homes may cook for one person, a couple, a group, roommates, recurring guests, or any other mix of eaters, and may need to support one or more dietary patterns without turning dinner into unrelated meals.

The app should support a configurable shopping day, prep-ahead window, serving counts, leftovers, dietary profiles, and weekday prep constraints without baking a single household's composition, diet, or favorite meals into source control.

## Users

- A household meal planner who chooses the weekly dinners and grocery list.
- Household members with configurable serving needs and dietary preferences.
- Household members who may need diet-specific substitutions without receiving an unrelated meal.
- Household members who may prefer simpler, familiar, lower-risk serving options.
- Optional household viewers who may check what dinner is planned.

## Goals

- Suggest five dinners per week from a configurable meal catalog.
- Prefer meals that have not been eaten as often, while allowing high-likability meals to appear more frequently.
- Never suggest the same meal more than once in a weekly plan.
- Make manual changes easy: replace meals, swap individual variation choices within a meal, reorder days, lock choices, and mark meals eaten or skipped.
- Track when meals and specific variation options were eaten so future suggestions can balance preference and variety at both the meal level and each variation dimension.
- Support configurable household members, serving counts, leftover needs, and dietary preferences.
- Support mixed-diet planning in two modes:
  - Separate-variation mode, where one shared meal can have diet-specific variation dimensions such as default protein and diet-compatible protein.
  - Common-compatible mode, where suggestions only include meals/options compatible with every active household dietary preference.
- Support shared-base meals where most ingredients are common and selected variations split by person, diet group, or preference.
- Support configurable leftover lunch servings and avoid consecutive similar leftover lunches when possible.
- Produce a Sunday grocery and prep view from the selected plan.
- Run locally first, with a path to Home Assistant packaging.
- Keep private household details, diet selections, meal preferences, meal history, and user-specific seed catalogs out of git by default.

## Non-Goals

- Do not build a native iOS app in the initial scope.
- Do not require a cloud account, external authentication provider, or public internet exposure.
- Do not optimize nutrition, calories, macros, or allergens in the initial scope.
- Do not support pantry inventory, price comparison, grocery delivery ordering, or barcode scanning in the initial scope.
- Do not try to fully automate household preference decisions; manual edits remain first-class.
- Do not require Home Assistant to run the development version, even though Home Assistant packaging is a likely deployment path.

## Success Criteria

- A user can open the web app and generate a five-dinner week from the starter catalog.
- A user can configure how many people they cook for, serving counts, and dietary preferences before using recommendations seriously.
- A user can choose whether mixed-diet households use separate diet-specific variations or only meals compatible with all configured diets.
- The generated week has five distinct meals.
- A user can replace any suggested meal and preserve locked meals during regeneration.
- A user can mark a whole week or specific days as vacation so no meals are planned on those dates.
- A user can choose independent variation options without changing the top-level meal, such as a protein, vegetable set, sauce, base, or preparation method.
- A user can mark planned meals as eaten, skipped, or moved.
- Eating history changes future suggestions in favor of underused meals and underused variation options, adjusted by likability.
- High-likability meals can recur more often over time but still no more than once in the same week.
- The weekly view clearly shows dinner, leftovers, prep-ahead tasks, and grocery-impacting ingredients.
- The grocery and prep view can be used for one Sunday shopping trip and 1-2 hours of prep.
- A git status check before commit does not include private database files, local household config exports, or user-specific meal catalogs.

## Key Decisions

- The initial app is a local-first standalone web app using FastAPI, SQLite, and static frontend assets.
- The Home Assistant model from MinuteMetrics is useful for packaging and local hosting, but the initial app should not be Home Assistant-only.
- The meal catalog is editable data, not hardcoded application behavior.
- Meal variation dimensions and options are first-class editable data beneath a meal, not just free-text notes.
- Suggestions are deterministic enough to explain with reason codes, but can include controlled randomness among similarly scored meals.
- Manual edits are part of the product model, not exceptions to the algorithm.
- Public source should describe generic household concepts. Any specific installed household's composition, diet configuration, meal selections, likability scores, and history belong in ignored local data, not tracked files.
