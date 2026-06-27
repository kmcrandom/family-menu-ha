# Recommendation Engine

## Purpose

The recommendation engine suggests five distinct dinners for a planning week. It should reduce decision fatigue while keeping the planner in control.

## Inputs

- Active meal catalog.
- Active meal variation dimensions and options.
- Existing weekly plan and locked meals.
- Vacation blocks for the selected weekly plan.
- Meal events and eaten dates.
- Meal likability.
- Variation-option likability.
- Household preferences.
- Household members and dietary profiles.
- Mixed-diet recommendation mode.
- Meal metadata such as prep time, leftover style, make-ahead score, and leftover quality.

## Hard Constraints

- Suggest only active meals.
- Suggest only active variation options unless preserving a historical planned meal.
- In common-compatible mode, suggest only meals and selected variation options compatible with every active household dietary profile.
- In separate-variation mode, ensure each active dietary profile can be assigned at least one compatible option for required diet-sensitive dimensions.
- Do not suggest the same meal more than once in a weekly plan.
- Preserve locked planned meals.
- Do not create planned meals on dates covered by a vacation block.
- If a whole week is blocked as vacation, generate no planned meals for that week.
- Preserve selected variation options when a planned meal is locked or reordered.
- Do not exceed `max_same_meal_per_week`, initially 1.
- Return the requested number of meals when enough active meals exist.

## Soft Preferences

- Prefer underused meals relative to their likability.
- Prefer underused variation options relative to their likability after a top-level meal is selected.
- Prefer meals not eaten recently.
- Prefer variation options not used recently when several options are available for a meal.
- Prefer meals with strong make-ahead scores for busier weeks.
- Prefer high leftover quality when configured leftover lunch servings are expected.
- Avoid scheduling the same `leftover_style` on consecutive dinner days when possible.
- Add variety across tags, such as not stacking too many sandwich meals or rice bowls in one week.

## Scoring Model

The first implementation should use a transparent weighted score:

- Likability score: normalized `likability`.
- Frequency balance score: meals eaten less often than expected are boosted.
- Recency score: meals eaten recently are penalized.
- Prep score: make-ahead and low active prep are boosted.
- Leftover score: leftover quality is boosted.
- Variety score: meals that diversify leftover style and tags are boosted.

The expected frequency for a meal should be proportional to likability across active meals. For example, a meal with likability 90 should naturally appear more often than a meal with likability 50, but both should still be considered if the higher-likability meal has been eaten repeatedly.

Variation scoring should use the same idea within each independent dimension of a meal. If a shared-base meal is selected, the primary protein dimension can score default options separately from a diet-compatible protein dimension, and sauce/base/vegetable dimensions can still be scored independently. This keeps a frequent meal from hiding underused compatible options.

## Dietary Compatibility

The engine should support two household modes:

- `separate_variations`: allow one shared-base meal to select separate compatible options for different dietary profiles. For example, one configured diet group may receive an unrestricted protein while another receives a vegetarian, vegan, pescatarian, or custom-compatible option.
- `common_compatible_only`: filter meal and option candidates so every selected item is compatible with all active household dietary profiles.

Compatibility should be driven by diet tags and dietary profile rules, not by hardcoded relationship assumptions or a single household's preferences.

## Reason Codes

Each suggestion should expose reason codes for the UI, such as:

- `high_likability`
- `underused`
- `not_recently_eaten`
- `good_leftovers`
- `prep_ahead_friendly`
- `locked_by_user`
- `leftover_variety`
- `underused_variation_option`
- `not_recently_used_variation_option`
- `variation_option_high_likability`

## Manual Overrides

- Replacing a meal should show eligible top-level meal alternatives sorted by recommendation score.
- Swapping a variation option should show eligible options within the same meal and dimension sorted by recommendation score.
- Regenerating a plan should preserve locked meals and fill only unlocked slots.
- Regenerating a plan should delete unlocked planned meals that fall on vacation dates and should not refill those dates.
- Regenerating variation options should optionally preserve top-level meals and refill only unlocked dimensions.
- The planner can choose a lower-scored meal without penalty; history should record what was actually eaten.

## Edge Cases

- If fewer active meals exist than requested slots, fill as many as possible and explain the shortage.
- If all meals are recent, choose the least-bad candidates and explain the recency tradeoff.
- If no history exists, use likability, prep, leftovers, and controlled variety.
- If a planned meal is skipped, it should not count as eaten.
- If a planned meal is eaten without required variation selections, count only the parent meal and prompt gently to select missing options next time.
- If common-compatible mode filters out too many meals, explain that the active catalog does not have enough compatible options and prompt the user to add compatible meals or switch to separate-variation mode.
- If separate-variation mode finds a meal without compatible options for one dietary profile, exclude that meal or mark the missing dimension clearly before planning.
- If vacation blocks leave fewer available dinner dates than the weekly target count, fill only the available dates and explain the shortage through the week status or empty state.

## Acceptance Criteria

- Repeated generation for the same inputs is stable enough to be understandable.
- Locked meals survive regeneration.
- A high-likability meal can appear more often across months than a lower-likability meal.
- A high-likability variation option can appear more often within its parent meal and dimension than a lower-likability option.
- No meal appears twice in the same generated week.
- No meal is generated on a vacation-blocked date.
- Variation-option history affects future option suggestions independently of meal history.
- Consecutive leftover-style repetition is avoided when enough alternatives exist.
- Common-compatible mode never suggests a meal or option that conflicts with an active dietary profile when enough compatible data exists.
- Separate-variation mode can choose distinct compatible options for configured diet groups within the same shared-base meal.
