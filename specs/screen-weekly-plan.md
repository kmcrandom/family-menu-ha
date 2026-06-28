# Weekly Plan Screen

## Purpose

The Weekly Plan screen is the primary workflow for selecting five dinners, assigning them to days, choosing variations, and marking what happened.

## Primary Content

- Selected planning week, initially the current week.
- Previous/current/next week controls so upcoming weeks can be planned before they start.
- Last viewed planning week for the current browser session.
- Five dinner slots by default.
- Vacation status for the selected week and any blocked dates.
- Meal name.
- Meal source link when one is configured.
- Selected variation options grouped by dimension.
- Planned date or order.
- Default or primary protein where applicable.
- Diet-compatible variation selections where applicable.
- Variation option details such as sauce, vegetables, pasta shape, or base when relevant.
- Muted color accents on variation controls, derived from the variation dimension key and consistent with Meal Catalog.
- Leftover lunch indicator.
- Prep-ahead summary.
- Suggestion reason codes.
- State: planned, eaten, skipped, or moved.

## Primary Actions

- Generate suggestions for the week.
- Open the next week and create it if needed.
- Return to the current week.
- Mark the whole selected week as vacation.
- Mark a specific planned date as vacation.
- Remove a vacation block.
- Regenerate unlocked meals.
- Lock or unlock a planned meal.
- Replace a meal.
- Swap a variation option within the selected meal.
- Open the meal source link.
- Open a cooking-instructions dialog for the planned meal.
- Reorder meals.
- Change planned date.
- Choose or edit variation.
- Mark eaten.
- Mark skipped.
- Move to another date.
- Open Grocery and Prep for the week.

## Manual Editing Requirements

- The user must be able to change any suggested meal.
- If a user navigates to another app screen and later returns to Weekly Plan, the screen should reopen to the last viewed week from the current browser session rather than always resetting to the current week.
- The Current Week action should still explicitly return the user to the current week and update the remembered Weekly Plan week.
- Week metadata, week navigation, generate/regenerate, and vacation controls should use compact toolbar-style rows on desktop and tablet.
- Meal rows should keep the date, meal picker, and primary row actions on the same horizontal line where space allows.
- The meal picker should have a constrained maximum width on desktop and tablet so long meal names do not consume the whole row.
- The meal picker should be anchored immediately to the right of the date block on desktop/tablet rather than drifting toward the center when row actions have available space.
- Meal rows should not show a generated variation-summary paragraph below the meal picker because the selected variation controls appear directly below the row header.
- Variation controls inside a planned meal should use multiple columns on desktop/tablet and collapse to one column on phone-sized screens.
- Variation controls inside a planned meal should use muted semantic colors so repeated dimension types are easier to scan across meal rows.
- Each variation control should keep the dimension label, selected option dropdown, and variation lock action inline horizontally on desktop/tablet.
- Variation controls should order their inline content as label, dropdown option, then lock icon.
- Variation controls should be vertically compact, avoiding excess empty padding above or below the label/select/icon row.
- The selected option text inside each variation dropdown should be vertically centered in the visible select field.
- Variation labels should remain readable and may be slightly larger than prior dense labels when the row height stays compact.
- Longer common variation labels, including `Primary protein` and diet-specific protein labels, may wrap to two short lines to reduce horizontal width and keep the dropdown close.
- The horizontal gap between the variation label and dropdown should be capped so compact labels do not create a large blank space before the option.
- Variation lock actions should use an icon-only lock/unlock button with an accessible name and tooltip instead of visible `lock` text.
- Small action buttons and lock controls should not force meal rows to become unnecessarily tall.
- Meal source links should be visible but compact, using an external-link style action when a meal has a source URL.
- The cooking-instructions action should open a dialog containing the meal instructions, selected option instructions when present, and the source link.
- The instructions dialog should include clear vertical spacing between the source-link button and the `Meal Instructions` section header.
- The instructions dialog should remain readable on phones and should not require navigating away from the weekly plan.
- Meal tags or label chips should not be shown on Weekly Plan meal rows; tag browsing and filtering belong in Meal Catalog.
- Weekly Plan should not show a labels `mat-chip-set` in meal rows, row footers, or recommendation summaries.
- The user must be able to change any selected variation option without changing the top-level meal.
- In separate-variation mode, the screen should show separate compatible selections for configured diet groups when a meal supports them.
- In common-compatible mode, the screen should only offer meals and variation options that satisfy all active household dietary profiles.
- Locked meals must remain unchanged during regeneration.
- Regenerating unlocked meals should be able to produce different unlocked meal and variation choices across repeated clicks, while staying within eligible, high-scoring recommendations.
- A variation dimension can be locked separately from the top-level meal if the user wants to keep a meal and one selected option while still regenerating another topping, base, sauce, protein, or side choice.
- Replacing a meal should offer alternatives sorted by recommendation score and explain why each is eligible.
- Swapping a variation option should offer options for the current meal and dimension sorted by option recommendation score and explain why each is eligible.
- Reordering should not erase selected variation options or notes.
- Marking a date as vacation should remove an existing planned meal for that date.
- Marking the whole week as vacation should remove all planned meals for the selected week.
- Marking a date or week as vacation should first show a confirmation dialog warning that existing planned meals on the affected date range will be deleted.
- The confirmation dialog should identify the affected date or week and offer clear Cancel and Confirm actions.
- Removing vacation mode should leave the week empty until the user explicitly generates or adds meals.

## Leftover Requirements

- Each planned dinner should show whether it is expected to produce the configured leftover lunch servings.
- If adjacent dinners have the same leftover style, the screen should warn gently and allow the plan anyway.
- The app should not force a leftover schedule unless the user chooses to track lunches explicitly later.

## Empty States

- No meal catalog: prompt to import starter meals or create a meal.
- No plan for selected week: show a generate action.
- Selected week is fully vacation: show a vacation empty state and hide meal generation until vacation mode is removed.
- Some selected dates are vacation: show those dates as blocked and omit them from generation.
- Not enough active meals: explain how many active meals are needed.

## Acceptance Criteria

- A user can generate a five-meal plan in one action.
- A user can view and edit next week's plan before the next week starts.
- A user can navigate from a future Weekly Plan week to another screen and back, and the future week remains selected.
- Switching weeks should not overwrite or regenerate an existing plan unless the user explicitly chooses to generate or regenerate it.
- A user can mark a whole week as vacation, which removes existing planned meals and prevents new meals from being generated for that week.
- A user can mark specific days as vacation, which removes existing planned meals for those days and prevents generation on those dates.
- A user sees and must confirm a warning before vacation mode deletes existing planned meals.
- A user can remove a vacation block and then manually generate/regenerate meals for the newly available dates.
- A user can manually replace any slot.
- A user can swap one variation option for a slot while preserving the top-level meal, date, and other selected options.
- A user can scan and edit variations in one compact horizontal row per dimension on desktop/tablet.
- Variation rows use less vertical space than card-like stacked controls while keeping label text legible.
- A user can lock or unlock a variation using only the lock icon while assistive technology still receives a clear label.
- A user can open meal instructions from a planned meal without leaving the Weekly Plan screen.
- A user can open the meal source link from a planned meal when one exists.
- Weekly Plan meal rows do not show meal tag/label chips.
- Weekly Plan does not render a labels chip set.
- Weekly Plan meal rows do not show a duplicate text summary of selected variations below the meal name or meal picker.
- Weekly Plan meal pickers remain left-aligned next to their date blocks.
- Variation dropdown selected-option text appears vertically centered within the field.
- Longer protein variation labels wrap cleanly without pushing the dropdown too far right.
- A user can visually scan variation types by consistent muted color, such as vegetables always using the vegetables color.
- A user can lock a slot, regenerate, and see the locked slot preserved.
- A user can click regenerate again with one or more unlocked slots and see the app explore a different valid recommendation when there are multiple strong eligible candidates.
- A user can see whether a recommendation is driven by the meal score, one or more variation-option scores, or both.
- A user can mark a planned meal eaten and create a history event.
- The screen remains useful on a phone-sized viewport.
- The desktop and tablet layouts show the week controls, vacation controls, and at least several planned meal rows with reduced vertical scrolling compared with a single-column stacked layout.
