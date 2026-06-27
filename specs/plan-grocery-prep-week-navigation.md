# Plan: Grocery and Prep Week Navigation

## Goal

Make Grocery and Prep target the upcoming shopping week by default while still allowing the user to move between weeks with the same previous/current/next model used by Weekly Plan.

## Implementation Steps

1. Grocery and Prep component state
   - Track `plan`, `grocery`, `loading`, `saving`, `error`, `currentWeekStartDate`, and `selectedWeekStartDate`.
   - On initial load, fetch the current plan to learn the current week start date.
   - Compute the next upcoming Sunday from the browser's current date.
   - Load that upcoming Sunday with `getPlanByWeek(weekStartDate)` instead of always rendering the current plan.
   - Keep checklist mutations scoped to the selected plan.

2. Grocery and Prep week navigation
   - Add `previousWeek`, `currentWeek`, `nextWeek`, and `isCurrentWeek` helpers matching Weekly Plan behavior.
   - Changing weeks should fetch or create the selected weekly plan and then fetch grocery/prep output for that plan.
   - Week navigation must not generate meals.

3. Grocery and Prep UI
   - Add compact week metadata and previous/current/next controls above the grocery/prep columns.
   - Show loading and empty/error states without losing the selected week context.
   - Preserve Angular Material buttons, icons, cards, checkboxes, and dark-mode styling.

4. Verification
   - Run `npm run build`.
   - Run the backend test suite to confirm existing API and checklist behavior still pass.
   - Browser-check Grocery and Prep:
     - It defaults to the next upcoming Sunday for the current local date.
     - Previous/current/next controls change the selected week.
     - Navigation does not generate meals.
     - The route renders cleanly in dark mode with no console errors.

## Risks and Notes

- The default week calculation is frontend-local and should use the user's browser date. Backend current-week logic remains unchanged for Weekly Plan.
- Opening Grocery and Prep may create an empty plan for the upcoming Sunday if it does not already exist, matching the existing selected-week API behavior.
- Checklist state remains keyed by weekly plan on the backend; no data migration is required.

## Non-Goals

- Calendar picker or arbitrary date input.
- Changing the backend definition of current week.
- Automatically generating meals for the selected Grocery and Prep week.
