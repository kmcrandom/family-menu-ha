# Web App Overview

## Navigation

The initial web app has five primary screens:

- Weekly Plan.
- Meal Catalog.
- Grocery and Prep.
- History.
- Settings.

The Weekly Plan screen is the default first screen. This is an app, not a marketing site.

## UX Principles

- Make the current week actionable at a glance.
- Keep manual editing faster than fighting the algorithm.
- Show diet-compatible variation choices as a normal part of a meal, not as a special exception.
- Keep simple serving variations visible but secondary.
- Treat Sunday prep and grocery shopping as part of the weekly planning workflow.
- Avoid dense configuration on the main screen.
- Prefer compact desktop and tablet layouts that reduce unnecessary vertical scrolling while staying readable.
- Keep small-value fields, such as percentages, minutes, counts, dates, and short labels, visually narrow instead of stretching them across the full available width.
- Put related controls on the same horizontal line on desktop and tablet when labels and values remain readable.

## Shared UI States

All screens should handle:

- Loading.
- Empty state.
- Validation errors.
- Save failures.
- Offline or server unavailable state.
- Archived or deleted meal references in history.

## Shared Interactions

- Meal names link to a meal detail/edit view.
- Screen navigation should preserve lightweight screen context where it prevents surprise resets, such as the last viewed Weekly Plan week and the last viewed Grocery and Prep week in the current browser session.
- Remembered screen context should be scoped by screen when workflows differ; for example, Weekly Plan and Grocery and Prep should keep independent selected-week memory.
- Meal source URLs open as external links when configured.
- Cooking instructions open in a Material dialog from planning contexts so the user does not lose their place.
- Likability is shown as a percentage.
- Variation-option likability is shown as a percentage where options are edited or compared.
- Tags are visible as compact labels.
- Tags or labels are selectable filters in catalog/search contexts, but should not clutter the Weekly Plan meal rows.
- Separate-variation mode shows relevant diet-compatible variation dimensions side by side.
- Common-compatible mode hides incompatible meal and option choices from normal suggestion lists.
- Top-level meal actions and variation-dimension actions are visually distinct.
- Actions that affect history, such as marking eaten, should be explicit.

## Component System

- The Angular frontend should use Angular Material as its primary component library.
- Use Material form fields, selects, inputs, buttons, button toggles, cards, chips, checkboxes, lists, tabs, toolbars, icons, progress indicators, snack bars, and dialogs where they fit the workflow.
- Keep native Angular templates and typed component state; do not add another frontend state library just for Material adoption.
- Keep screen density compact and operations-focused. Material components should be styled and composed for repeated household planning work, not for a marketing or showcase layout.
- Use Material theming tokens for the base color system and keep app-specific layout CSS for grids, spacing, responsive behavior, and row-level planning surfaces.
- Prefer Material icons for common actions such as previous, next, lock, archive, delete, add, save, grocery, history, and settings.
- Use Material dialogs for destructive confirmations, including vacation actions that delete planned meals.
- Use Material dialogs for read-only recipe or meal instruction popups.
- Use icon-only Material buttons for compact repeated actions such as row movement, meal locks, variation locks, source links, and instruction popups when the icon has a clear tooltip and accessible name.
- Dark mode is the default visual theme.
- The dark theme should preserve the app's calm, operational feel with high-contrast text, subdued surfaces, visible dividers, and clear selected/blocked states.
- If a light theme is added later, it should be a user-selectable alternate theme, not the default.
- Add muted semantic accent colors for repeated planning concepts, especially variation dimensions, without making the app feel bright or playful.
- Semantic colors must be consistent across screens. For example, vegetables should use the same muted green treatment in Weekly Plan and Meal Catalog.
- Color must reinforce labels, not replace them. Every colored variation section still needs visible text labels and accessible names.

## Variation Color Semantics

Variation dimensions should use a stable muted color treatment derived from their dimension key:

- `variation_primary_protein`: muted warm red or clay.
- `variation_diet_protein` or diet-compatible protein dimensions: muted teal or blue-green.
- `variation_vegetables`: muted green.
- `variation_sauce`: muted amber.
- `variation_starch_or_base`, `variation_base`, or pasta/base dimensions: muted blue or indigo.
- `variation_toppings`: muted rose.
- `variation_prep_method`: muted slate.
- Unknown custom variation keys: subdued neutral accent.

The same key should receive the same color on Weekly Plan meal rows, Meal Catalog dimension cards, and any future compact variation summaries.

## Responsive Density

- Optimize first for desktop and tablet screens because planning and catalog editing are repeated operations that benefit from seeing more context at once.
- Preserve phone usability by collapsing multi-column groups into a single column below the mobile breakpoint.
- Use responsive grid classes for common field widths:
  - Short fields for percentages, minutes, numeric counts, and compact select controls.
  - Medium fields for names, category labels, profile labels, dates, and mode selectors.
  - Wide fields for notes, instructions, ingredient lists, prep task lists, and search.
- Avoid full-width Material fields for small values unless the viewport is narrow.
- Keep related page controls grouped into compact toolbar rows where possible, including week navigation, filters, primary actions, and mode selectors.
- Avoid nested cards and oversized padding; page sections should remain scannable without looking cramped.
- On tablet-width screens, prefer two-column layouts for independent sections and two-to-four-column field grids where labels fit.
- On phone-width screens, keep controls finger-friendly, preserve visible labels, and avoid horizontal overflow.
- Dense layout changes should not hide important state such as errors, vacation blocks, checked items, archived status, or save progress.

## Accessibility

- Controls must be keyboard reachable.
- Buttons must have visible labels or accessible names.
- Color cannot be the only way to distinguish meal status.
- Text must fit on mobile and desktop viewports.
- Material controls should preserve labels, accessible names, focus states, and validation messaging after refactor.
- Dark mode contrast must remain readable for form fields, dialogs, chips, blocked vacation states, disabled controls, and checklist rows.

## Initial Visual Direction

The UI should feel like a practical household operations tool: calm, scannable, compact, and dark by default. It should avoid a decorative landing-page layout and prioritize the weekly plan, editable rows, and clear controls. Angular Material should provide the component foundation, while the app-specific layout should keep meal planning dense enough for scanning and manual editing.
