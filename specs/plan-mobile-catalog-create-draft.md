# Plan: Blank Meal Drafts and Mobile Catalog Menu

## Goal

Make new meal creation feel empty until the user enters values, and keep the Meal Catalog list out of the main phone layout behind a slide-over menu that also owns the Create meal action.

## Implementation Steps

1. New meal draft form values
   - Update `family-menu/frontend/src/app/meal-catalog/meal-catalog.component.ts`.
   - Change the reactive form and `defaultMealFormValue()` so new drafts reset numeric controls to `null` or an empty value instead of `80`, `20`, `50`, or `70`.
   - Keep placeholders/labels in the template, but do not show numeric defaults in a new draft.
   - Adjust `mealPayloadFromForm()` so blank numeric controls are omitted from the create payload instead of being converted to default values. Existing API defaults may still be used by the backend after save.
   - Preserve existing patch behavior for saved meals so editing a persisted meal continues to send explicit numeric values.
   - Keep `newMealDraft()` compatible with the `Meal` view model while ensuring the form, not the draft object, controls what the user sees.

2. Mobile slide-over state and interactions
   - Add component state for opening and closing the meal menu on phone-sized layouts.
   - Close the menu after selecting a meal or starting Create meal.
   - Keep existing draft-discard confirmation behavior when switching away from an unsaved new meal.

3. Catalog list template refactor
   - Update `family-menu/frontend/src/app/meal-catalog/meal-catalog.component.html`.
   - Extract the meal menu/list controls into a reusable template rendered both as the desktop side panel and the phone slide-over content.
   - Add a compact menu icon button near the Meal Catalog heading for phone-sized screens.
   - Keep Create meal with the list/search controls, not inside the editor detail pane.
   - Add an overlay/backdrop and close button for the slide-over.

4. Responsive styling
   - Update `family-menu/frontend/src/styles.css`.
   - Keep the current visible side panel on desktop/tablet.
   - Hide the side panel on phone-sized screens and show the menu icon.
   - Style the phone slide-over with stable width constraints, a backdrop, scrollable list content, and no overlap with the editor.
   - Confirm buttons and headings fit at phone widths.

5. Tests and verification
   - Run `npm run build` in `family-menu/frontend`.
   - Run focused backend tests only if payload changes require backend contract validation; otherwise no backend change is expected.
   - Start the local app and verify in a browser at desktop and phone widths:
     - New meal numeric fields are blank before entry.
     - Desktop still shows the catalog side panel and Create meal there.
     - Phone hides the catalog list by default, opens it from a menu icon, includes Create meal in the slide-over, and closes the slide-over after selecting or creating.

## Risks and Notes

- This plan intentionally keeps backend create defaults unchanged, so saving a meal with omitted numeric fields can still receive the existing persisted defaults from the API.
- The user-visible requirement is that the new meal form does not display default values before input.
- The drawer will be implemented with existing Angular/Material primitives and CSS rather than adding a new dependency.
