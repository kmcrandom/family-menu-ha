# Plan: Weekly Plan Navigation

## Goal

Let a user view and edit next week's meal plan before the next week starts, without changing the existing current-week workflow or accidentally regenerating plans.

## Scope

- Add week navigation controls to the Weekly Plan screen.
- Use the existing `GET /api/v1/plans?week_start_date=YYYY-MM-DD` endpoint to fetch or create a selected week.
- Keep plan generation manual: navigating to next week should create an empty plan if needed, but should not generate meals until the user clicks Generate Week.
- Keep Grocery and Prep tied to the selected week.

## Implementation Steps

1. Frontend API
   - Add `getPlanByWeek(weekStartDate: string)` to `ApiService`.
   - Keep `getCurrentPlan()` unchanged for the initial load/current-week shortcut.

2. Weekly Plan component state
   - Track the currently selected week start date.
   - Track the current week start date from the first `getCurrentPlan()` response.
   - Add helpers to compute previous and next Sunday-based week dates from the selected plan.
   - Add `loadPlanForWeek(weekStartDate)` that reuses the meal catalog already loaded when possible.
   - Update mutation reloads (`patch`, `move`, `markEaten`, `skip`) to reload the selected week rather than always returning to current week.

3. Weekly Plan UI
   - Add compact `Previous`, `Current Week`, and `Next` controls near the week metadata.
   - Show the selected week and shopping date as today.
   - Disable controls while saving/loading to avoid overlapping writes.
   - Preserve the existing Generate/Regenerate button behavior for whichever week is selected.

4. Verification
   - Run frontend build.
   - Run backend tests if any shared behavior changes; otherwise use existing API behavior.
   - Browser-smoke-test:
     - Open current Weekly Plan.
     - Click Next.
     - Confirm the displayed week advances to Sunday, June 28, 2026 on the current local date.
     - Confirm an empty next-week plan can be generated manually.
     - Click Current Week and confirm it returns to Sunday, June 21, 2026 without overwriting either plan.

## Risks

- Date parsing must avoid timezone off-by-one issues. Use local date construction from `YYYY-MM-DD` parts rather than parsing midnight UTC date strings directly.
- Existing mutation methods currently call `load()`, which would return to current week. They must reload the selected week instead.
- Generating the next week in the local DB is user data. Browser verification can create the next-week plan intentionally, but should not overwrite current-week data.

## Non-Goals

- Automatic scheduled plan generation.
- Calendar picker or arbitrary date selection beyond previous/current/next controls.
- Changing week-start-day behavior beyond the current Sunday-based implementation.
