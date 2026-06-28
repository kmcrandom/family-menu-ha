# Plan: Randomized Regeneration

## Goal

Let explicit regeneration of unlocked weekly plan items explore different valid recommendations while keeping selections score-driven, constraint-safe, and understandable.

## Scope

- Backend recommendation selection for unlocked meals.
- Backend variation-option selection for unlocked, regeneratable variation dimensions.
- Focused tests proving randomness can change unlocked selections and that locks/hard constraints remain intact.

## Implementation Steps

1. Add controlled random candidate selection in `family-menu/src/family_menu/recommender.py`.
   - Keep existing scoring functions and reason codes.
   - Sort candidates by score and name as today.
   - Build a top-candidate window from the strongest few candidates and/or candidates within a modest score distance of the best score.
   - Randomly choose within that bounded window.

2. Apply the same bounded candidate helper to variation options.
   - Preserve locked variation dimensions.
   - Preserve existing variation selections when `regenerate_variations` is false.
   - Randomize only when the dimension is eligible for regeneration and has multiple strong active options.

3. Keep hard constraints unchanged.
   - Active meal and option filtering remains before random selection.
   - Used meals still prevent duplicates in the generated week.
   - Vacation-blocked dates remain skipped.
   - Dietary compatibility filters remain before scoring.
   - Locked meals remain inserted unchanged.

4. Add focused automated tests.
   - Unit-level tests for candidate-window behavior with monkeypatched randomness so results are deterministic in the test suite.
   - API/recommender tests that repeated generation can alter unlocked meals when there are multiple candidates.
   - Existing locked-meal and dietary/vacation tests should continue to pass.

5. Run verification.
   - Run `pytest tests/test_recommender.py tests/test_api.py`.
   - If failures indicate shared behavior changed, run the full Python test suite.

## Risks and Compatibility

- Randomness can make broad snapshot-style tests flaky if tests assert exact meal order. Existing tests mostly assert constraints, but any exact-order assumptions should be updated to assert invariant behavior instead.
- The bounded candidate window should be conservative so low-scoring meals do not appear merely because the user clicked regenerate.
- No database migration, API contract change, frontend change, or persisted seed is planned.

## Non-Goals

- No UI controls for randomness strength.
- No seeded deterministic replay.
- No change to manual replacement sorting.
- No change to history scoring weights.
