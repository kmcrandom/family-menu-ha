# Plan: Meal Catalog Label Filter

## Goal

Move Meal Catalog label filtering out of the persistent chip section below the list and into the search area, while tightening the catalog list placement so it aligns with the editor on wider screens.

## Implementation Steps

1. Search-area filter control
   - Replace the persistent `tag-filter` chip section in `meal-catalog.component.html` with a compact filter icon button in the search field suffix area.
   - Keep the existing search icon visible or otherwise preserve the search affordance.
   - Use a Material menu opened by the filter icon to show available labels.
   - Include an all/clear option when a label filter is active.
   - Show the selected label near the search field in a compact, clearable control so the active filter is visible without the old chip section.

2. Label filtering behavior
   - Reuse the existing `availableTags`, `selectedTag`, `selectTag`, and `clearTagFilter` behavior where practical.
   - Keep text search and label filtering composable.
   - Preserve archived-meal filtering behavior for available labels.
   - Ensure meals remain filtered immediately when a menu option is selected.

3. Material imports
   - Add `MatMenuModule` to `family-menu/frontend/src/app/shared/material.ts` if needed by the new menu.
   - Avoid adding new dependencies.

4. Layout and responsive styling
   - Remove obsolete `.tag-filter` styling or replace it with scoped search/filter styles in `styles.css`.
   - Add styles for the search field suffix actions, selected-label display, and menu items so labels wrap/truncate cleanly.
   - Adjust catalog list layout/sticky positioning so the `catalog-list` card starts at the top of the catalog grid and aligns with the editor card on desktop/tablet.
   - Keep the single-column phone layout free of horizontal overflow and avoid a persistent label area below the meal list.

5. Verification
   - Run the frontend build from `family-menu/frontend`.
   - Browser-check Meal Catalog on a desktop-sized viewport:
     - catalog list card top aligns with the editor card
     - filter icon opens the label list
     - selecting a label filters meals
     - clearing the label restores the list
   - Browser-check Meal Catalog on a phone-sized viewport:
     - no persistent label chip section appears below the list
     - the filter menu/list is usable and not cut off
     - no horizontal overflow

## Risks and Notes

- Material menu content may need width constraints so long labels do not overflow on narrow screens.
- The existing `mat-chip-set` import remains used elsewhere, so removing this one chip set should not remove `MatChipsModule`.
- If the search-field suffix becomes visually crowded, the implementation may use adjacent compact icon buttons while keeping the filter action in the search area.

## Non-Goals

- Data model or API changes.
- Adding multi-select label filtering.
- Changing label taxonomy or meal tag editing.
- Redesigning the full Meal Catalog editor.
