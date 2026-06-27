# Plan: Weekly Plan Alignment Tweaks

## Goal

Keep the Weekly Plan meal picker anchored next to the date block, vertically center selected variation dropdown text, and let long protein labels wrap to two lines so variation controls use horizontal space better.

## Implementation Steps

1. Row header anchoring
   - Adjust Weekly Plan row header CSS so the date block and meal picker form a left-aligned group.
   - Prevent the meal picker from drifting toward the center when row actions have extra space.
   - Keep row actions aligned to the right on desktop/tablet.
   - Preserve full-width usability on phone-sized screens.

2. Variation label wrapping
   - Update variation label CSS to allow controlled wrapping.
   - Prefer two-line wrapping for long labels such as `Primary protein` and diet-specific protein labels.
   - Keep short labels compact and avoid pushing dropdowns right.

3. Variation select vertical centering
   - Adjust scoped Material select CSS inside Weekly Plan variation controls.
   - Center selected option text vertically in the visible field.
   - Keep row height compact and avoid disturbing other forms in Meal Catalog, Settings, or Grocery + Prep.

4. Verification
   - Run `npm run build`.
   - Run `.venv/bin/python -m pytest -q`.
   - Browser-check Weekly Plan desktop:
     - meal picker left edge sits immediately after the date block
     - row actions stay on the right
     - protein labels wrap to two lines
     - selected variation option text is vertically centered
     - no horizontal overflow
   - Browser-check Weekly Plan phone:
     - meal picker remains usable
     - variation rows stay readable without overflow
   - Check console errors and run the privacy scan.

## Risks and Notes

- Angular Material select internals are sensitive to height overrides, so centering styles should be scoped to `.variation-grid` only.
- Wrapping label text can increase row height for long labels; this is acceptable if it keeps the section compact overall and avoids wasted horizontal space.

## Non-Goals

- Changing recommendation behavior.
- Changing meal data or labels.
- Redesigning the entire Weekly Plan row.
