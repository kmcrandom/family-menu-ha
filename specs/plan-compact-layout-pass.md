# Plan: Compact Layout Pass

## Goal

Reduce unnecessary vertical scrolling across the Angular app by tightening field widths, grouping related controls into desktop/tablet rows, and preserving readable phone layouts.

## Implementation Steps

1. Shared layout utilities
   - Add reusable CSS classes for compact responsive form grids:
     - short fields for small numeric values and short selects.
     - medium fields for names, dates, and mode selectors.
     - wide/full fields for notes, ingredient lists, prep lists, and search.
   - Reduce excessive panel, row, checklist, and section gaps where the UI currently feels airy rather than useful.
   - Keep Material form fields full-width within their assigned grid cell, but stop small grid cells from stretching across whole rows on desktop/tablet.
   - Preserve the existing dark Material theme and phone breakpoints.

2. Weekly Plan
   - Combine week metadata and previous/current/next navigation into a compact planning toolbar.
   - Keep vacation controls compact and adjacent to week context.
   - Tighten planned-meal card padding/gaps and make row actions wrap less aggressively on desktop/tablet.
   - Preserve mobile stacking, vacation confirmations, meal replacement, variation controls, lock controls, and side rail behavior.

3. Meal Catalog
   - Rework the meal edit form into a denser grid:
     - name and leftover style as medium/wide fields.
     - likability, prep minutes, cook minutes, make-ahead, and leftover quality as short fields.
     - ingredients, prep tasks, and notes as full-width text areas.
   - Keep the catalog master/detail layout on desktop/tablet with a practical sidebar width.
   - Tighten variation option editors:
     - option name, likability, and archive/restore action on one row.
     - grocery additions, omissions, and option prep tasks in a three-column row on desktop/tablet.
   - Preserve line-based editing behavior.

4. Grocery and Prep
   - Combine week metadata and week navigation into one compact toolbar.
   - Tighten checklist row spacing and group spacing.
   - Keep grocery and prep columns side by side on desktop/tablet and stacked on phones.

5. History
   - Make the Add Event panel more compact by putting meal, date, and action in one responsive row on desktop/tablet.
   - Tighten recent event rows while preserving meal name, selected options, date, and delete action.
   - Keep phone rows readable and non-overflowing.

6. Family Config
   - Rework Planning Defaults into grouped compact rows:
     - household name and mixed-diet mode as wide/medium fields.
     - week/shopping day, counts, servings, repeat gap, and weights as short/medium fields.
   - Make household member editors denser by assigning name/profile as medium fields and serving counts as short fields.
   - Make dietary profile editors denser by assigning name/type as medium fields and tags as wide fields.
   - Keep add-member and add-profile rows compact on desktop/tablet and stacked on phones.

7. Verification
   - Run `npm run build`.
   - Run `.venv/bin/python -m pytest -q` to confirm no API regressions.
   - Browser-check all primary routes in dark mode:
     - Weekly Plan.
     - Meal Catalog.
     - Grocery + Prep.
     - History.
     - Family Config.
   - Browser-check desktop, tablet-width, and phone-width layouts for:
     - no horizontal overflow.
     - readable form labels and values.
     - no overlapping controls.
     - compact rows visible on desktop/tablet.
   - Keep browser QA read-only except for non-destructive route navigation.

## Risks and Notes

- Angular Material form fields have intrinsic spacing; the compact pass should reduce layout waste without overriding Material internals so heavily that labels, hints, or focus states break.
- Meal Catalog and Family Config have the highest risk of cramped text because they contain long labels and newly added grocery/prep editors.
- Some pages may need semantic wrapper classes in templates so global CSS does not accidentally affect unrelated controls.
- The layout pass should not change data models, API contracts, recommendation behavior, grocery generation, or saved local data.

## Non-Goals

- New features or fields.
- Replacing Angular Material.
- Adding a theme switcher.
- Changing desktop navigation structure.
- Creating a completely new visual design.
