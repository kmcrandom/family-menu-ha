# Plan: Catalog Labels and Weekly Density Tweaks

## Goal

Refine the Meal Catalog and Weekly Plan layout after recipe links/instructions were added, keeping the UI compact and easier to scan.

## Implementation Steps

1. Meal Catalog label placement
   - Move the label/tag filter chip section below the meal list in the left catalog panel.
   - Keep search at the top of the panel and the meal list immediately below search.
   - Preserve existing label filter behavior and clear action.
   - Keep the label section compact and usable when the list is long.

2. Meal Catalog source URL open action
   - Add a compact open-in-new-tab button next to or inside the Source URL field area.
   - Show the action only when the selected meal has a source URL or the current form value has a URL.
   - Open with `target="_blank"` and `rel="noopener noreferrer"`.
   - Keep the existing header source-link action unless it becomes visually redundant during implementation.

3. Weekly Plan label chip removal
   - Remove the recommendation/label `mat-chip-set` from Weekly Plan meal row footers.
   - Preserve action buttons such as Skip and Mark Eaten.
   - Confirm no label chip set remains in Weekly Plan rows.

4. Weekly Plan meal picker width
   - Constrain the meal name dropdown width on desktop/tablet so it does not consume the whole row.
   - Keep it responsive and usable on phone-sized screens.
   - Preserve long-name readability through truncation or normal Material select behavior.

5. Weekly Plan variation density
   - Reduce vertical padding and Material field height for variation controls.
   - Slightly increase variation label font size while keeping row height compact.
   - Reduce the maximum blank space between label and dropdown by using a tighter grid/flex layout.
   - Keep order as label, dropdown, lock icon.
   - Preserve muted semantic colors and accessible lock icon labels/tooltips.

6. Cooking instructions dialog spacing
   - Add vertical space between the source-link button and the `Meal Instructions` section header.
   - Keep the dialog readable on desktop and phone.

7. Verification
   - Run `npm run build`.
   - Run `.venv/bin/python -m pytest -q` if backend files are touched; otherwise run at least frontend build plus existing full suite if time is reasonable.
   - Browser-check Weekly Plan desktop and phone:
     - no label/recommendation chip set in meal row footer
     - meal dropdown width is constrained on desktop and full/usable on phone
     - variation rows are compact, inline, and without horizontal overflow
     - instruction dialog spacing looks correct
   - Browser-check Meal Catalog:
     - labels appear below the meal list
     - label filter still reduces the list
     - source URL open action appears near the URL field
     - no horizontal overflow
   - Run the privacy scan over tracked candidate files.

## Risks and Notes

- Angular Material form fields have default density and subscript spacing; CSS overrides should stay scoped to Weekly Plan variation controls to avoid disturbing forms elsewhere.
- Removing row-footer chips may also remove recommendation reason visibility from Weekly Plan. That is acceptable for this request because the user asked to remove labels/chips from the page.
- The source URL open action should use the current saved URL or form value without creating a save side effect.

## Non-Goals

- Data model changes.
- Recipe link lookup changes.
- New label taxonomy.
- Redesigning the full Weekly Plan row beyond the requested density and width adjustments.
