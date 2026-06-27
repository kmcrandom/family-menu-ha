# Plan: Remember Viewed Weeks

## Goal

Preserve the last viewed week when navigating away from Weekly Plan or Grocery and Prep, while keeping the remembered weeks independent for each screen.

## Implementation Steps

1. Weekly Plan remembered week
   - Add a small session-scoped storage key for Weekly Plan, such as `family-menu.weekly-plan.week-start`.
   - On initial Weekly Plan load, use the stored week if present; otherwise load the current plan as today.
   - Whenever the user navigates with Previous, Current Week, Next, or otherwise loads a week, update the Weekly Plan storage key.
   - Keep existing current-week calculation and API calls unchanged.

2. Grocery and Prep remembered week
   - Add a separate session-scoped storage key for Grocery and Prep, such as `family-menu.grocery-prep.week-start`.
   - On initial Grocery and Prep load, use the stored week if present; otherwise use the existing next-upcoming-Sunday default.
   - Whenever the user navigates with Previous, Current Week, or Next, update the Grocery and Prep storage key.
   - Do not read from or write to the Weekly Plan storage key.

3. Route/navigation behavior
   - Keep the state client-side in `sessionStorage` so it persists across app screen navigation in the same browser session without adding backend fields.
   - If a stored value is missing or invalid, fall back to the existing default for that screen.
   - Avoid regenerating plans when restoring a remembered week; only load or create the corresponding weekly plan record as the current screen already does.

4. History Add Event spacing
   - Add scoped spacing between the History `Add Event` section header and the Meal dropdown below it.
   - Preserve the current compact History layout and phone stacking behavior.

5. Tests and verification
   - Run `npm run build`.
   - Run `.venv/bin/python -m pytest -q`.
   - Browser-check Weekly Plan:
     - navigate to next week
     - go to Meal Catalog
     - return to Weekly Plan
     - confirm the next week remains selected
   - Browser-check Grocery and Prep:
     - navigate to a different week
     - go to Meal Catalog
     - return to Grocery and Prep
     - confirm the changed week remains selected
   - Browser-check independence:
     - set Weekly Plan to one week and Grocery and Prep to another
     - navigate between screens
     - confirm each screen keeps its own selected week
   - Browser-check History Add Event:
     - confirm the header and Meal dropdown have visible spacing and no overlap
   - Check browser console errors and horizontal overflow where practical.
   - Run the privacy scan.

## Risks and Notes

- `sessionStorage` is browser-tab scoped and clears when the browser session ends; that matches the requested navigation behavior without making this a permanent user preference.
- This should not change the default first visit behavior: Weekly Plan opens current week, Grocery and Prep opens the next upcoming shopping week.
- A malformed stored date should be ignored safely.

## Non-Goals

- Backend database changes.
- Permanent cross-device preference sync.
- URL query parameters or deep links for specific weeks.
- Changing recommendation or grocery generation behavior.
- Redesigning the History screen beyond the Add Event spacing tweak.
