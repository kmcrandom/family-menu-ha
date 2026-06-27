# Plan: Default Dark Mode

## Goal

Make dark mode the default visual theme for the Angular Material frontend while preserving the compact, operational meal-planning workflow.

## Scope

- Replace the current light Material prebuilt theme with a dark Material theme.
- Update app CSS variables to dark defaults.
- Tune cards, toolbar, panels, chips, vacation blocked states, notices, form fields, and list rows for readable dark-mode contrast.
- Keep the app dark by default without adding a theme toggle in this change.

## Implementation Steps

1. Material theme
   - Switch the global Angular Material theme import from a light prebuilt theme to a dark prebuilt theme or equivalent dark theme configuration.
   - Set `color-scheme: dark`.

2. CSS tokens
   - Change `:root` variables for background, surfaces, text, muted text, borders, accent, warning, danger, shadows, and soft states.
   - Update app-specific classes that currently assume light surfaces.
   - Ensure blocked vacation chips/buttons remain visible without relying on low-contrast amber-on-light styling.

3. Component cleanup
   - Check Material cards, form fields, selects, dialogs, checkboxes, chips, toolbar, icon buttons, and disabled states against the new dark tokens.
   - Keep density compact; do not increase spacing just because Material defaults are larger.

4. Verification
   - Run Angular production build.
   - Run backend tests as a regression check.
   - Browser-smoke-test:
     - Weekly Plan renders dark by default.
     - Vacation confirmation dialog is dark and readable.
     - Meal Catalog, Grocery + Prep, History, and Family Config render without console errors.
     - Mobile-width Weekly Plan still shows navigation, vacation controls, and meal rows without obvious clipping or overlap.

## Risks

- Some custom classes may retain light backgrounds and clash with Material dark components.
- Disabled states and muted text can become too low contrast if tokens are too subtle.
- Material prebuilt dark theme may not match the app palette perfectly; app-level CSS variables may need tuning.

## Non-Goals

- Adding a light/dark toggle.
- Persisting user theme preference.
- Redesigning layout or behavior.
- Changing backend APIs, data models, or recommendation logic.
