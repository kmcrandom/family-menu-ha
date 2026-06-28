# Plan: Variation Add and Color Popup UX

## Goal

Refine the Meal Catalog variation editing flow so add-variation controls are hidden until requested, the add entry point appears below current variations, and existing variation colors are changed through a compact color dropper popup instead of inline palettes.

## Implementation Steps

1. Add-flow state
   - Add component state to track whether the add variation controls are open.
   - Reset the add variation controls and close the add panel when selecting a different meal, canceling edit mode, or successfully adding a dimension.
   - Keep the existing reusable variation type, custom key, required flag, and color selection logic.

2. Move and gate add variation UI
   - Move the add variation UI in `meal-catalog.component.html` from above `.dimension-stack` to below the active variation list.
   - Replace the always-visible add fields with a single `Add variation` button while editing.
   - When activated, show the existing add fields in a compact expanded panel below the button.
   - Include a cancel/close action for the expanded add panel.
   - Preserve validation that prevents adding a dimension without a type and non-empty name.

3. Existing variation color popup
   - Remove the inline color swatch row and custom color input from each existing variation header.
   - Add a compact icon button using the Material `colorize` icon, with tooltip and accessible label.
   - Use a Material menu popup from that button to show preset swatches and a custom color input for that dimension.
   - Keep the existing required checkbox and remove/archive icon behavior.
   - Continue filtering duplicate preset colors already used by active dimensions, while allowing the dimension's current preset color to remain selectable/visible in its own popup.

4. Styling
   - Update shared CSS for the add panel, collapsed add button row, color popup, and compact icon alignment.
   - Keep desktop/tablet variation headers on one readable row where practical.
   - Ensure phone-sized layouts stack without horizontal overflow.
   - Keep current muted variation tone rendering for dimension cards and option editors.

5. Verification
   - Run `npm run build` in `family-menu/frontend`.
   - Browser-check Meal Catalog desktop:
     - existing variations appear before the Add variation button
     - add type/name/key/color controls are hidden until Add variation is clicked
     - existing dimension headers do not show inline color palettes
     - colorize icon opens a color popup and selecting a color updates the dimension accent
   - Browser-check Meal Catalog phone width for no overlap or horizontal overflow.

## Risks and Notes

- Material menus are available through the existing shared Material imports, so this should not require a new dependency.
- Native `<input type="color">` inside a menu may close the menu differently across browsers. If that proves awkward, use an explicit small menu section with a labeled color input and accept the native picker behavior.
- Duplicate preset filtering needs to include the current dimension's color in its own menu so users can see the selected state.

## Non-Goals

- Backend schema or API changes.
- Changing variation option editing behavior.
- Changing recommendation behavior.
- Replacing archive confirmations or option archive/restore behavior.
