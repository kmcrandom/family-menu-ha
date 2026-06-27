# Plan: Angular Material Refactor

## Goal

Refactor the Angular frontend to use Angular Material as the primary component system while preserving the current local-first app behavior, compact planning workflow, and vacation-mode safeguards.

## Scope

- Add Angular Material and Material icons to the Angular app.
- Configure a Material theme.
- Refactor the main app shell and primary screens to use Material components.
- Replace destructive vacation actions with Material confirmation dialogs that warn meals will be deleted.
- Keep FastAPI, SQLite, recommendation behavior, and API contracts unchanged except where frontend code needs typed API support already present.

## Implementation Steps

1. Dependencies and theme
   - Add `@angular/material`, `@angular/cdk`, and `@angular/animations` versions compatible with Angular 22.
   - Add Material Icons font or equivalent Material icon support.
   - Configure Material theme styles in the Angular stylesheet.
   - Keep app-specific CSS for layout density, grids, planner rows, responsive behavior, and print-free operational surfaces.

2. Shared app shell
   - Refactor top navigation to use Material toolbar/buttons/icons.
   - Keep the existing routes and URL structure.
   - Add Material progress indicators for loading states where appropriate.
   - Use Material snack bars or notices for save/error feedback when practical.

3. Weekly Plan screen
   - Use Material buttons, icon buttons, cards, chips, selects, form fields, checkboxes, and progress indicators.
   - Preserve week navigation, generate/regenerate, meal replacement, variation selection, locking, reorder, mark eaten, skip, grocery/prep side rail, and vacation mode.
   - Add a Material dialog before creating a vacation block.
   - The dialog must identify the affected date or week and state that existing meals in that range will be deleted.
   - Continue to allow ending vacation mode without a destructive warning because it does not recreate or delete meals.

4. Meal Catalog screen
   - Use Material list/card patterns for meal selection and details.
   - Use Material form fields, selects, buttons, chips, and expansion-style grouping where useful for variation dimensions and options.
   - Preserve archive/restore, meal editing, dimension editing, and option editing.

5. Grocery and Prep screen
   - Use Material cards, lists, checkboxes, and chips.
   - Preserve checked-state persistence.

6. History screen
   - Use Material form fields, selects, cards/list rows, buttons, and icons.
   - Preserve manual event creation and delete behavior.

7. Family Config screen
   - Use Material form fields, selects, cards, buttons, checkboxes, and chips/lists.
   - Preserve household members, dietary profiles, mixed-diet mode, planning defaults, and export link.
   - Keep local filesystem paths hidden.

8. Verification
   - Run Angular production build.
   - Run backend test suite to ensure static build and API contracts still work.
   - Browser-smoke-test:
     - App loads with Material shell and no console errors.
     - Weekly Plan controls render and week navigation works.
     - Vacation Week opens a confirmation dialog before deleting meals.
     - Cancel keeps meals unchanged.
     - Confirm applies vacation mode and removes affected meals.
     - Family Config still shows configured household members and dietary profiles.
   - Check mobile-width rendering for no obvious clipping or overlap on the main weekly workflow.

## Risks

- Angular Material 22 package availability may require network access and must match the Angular 22 peer dependency range.
- Material form-field markup can increase vertical density; CSS may need tuning to keep the app compact.
- Dialog verification may require careful browser automation because confirming vacation mode mutates the local ignored database.
- Existing custom CSS may conflict with Material component styles; prefer deleting or narrowing custom button/form styles rather than fighting Material defaults.

## Non-Goals

- Redesigning the recommendation engine.
- Changing backend data models beyond already-approved vacation behavior.
- Introducing a third-party state-management library.
- Adding authentication, cloud services, analytics, or non-local dependencies at runtime.
- Reworking the app into a marketing-style landing page.
