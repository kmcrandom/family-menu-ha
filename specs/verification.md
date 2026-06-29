# Verification Plan

## Backend Verification

- Validate meal schema creation and updates.
- Validate `POST /api/v1/meals` creates a meal with generated unique id, active status, default values, persisted editable fields, and an empty variation list.
- Validate meal creation rejects empty or whitespace-only names without inserting a row.
- Validate meal source URL, source name, and instructions persist through create/update/read flows.
- Validate weekly plan creation.
- Validate suggestion generation with no history.
- Validate suggestion generation with history.
- Validate locked meals are preserved during regeneration.
- Validate locked variation dimensions are preserved during meal reordering or variation-option regeneration.
- Validate no duplicate meal appears in the same generated week.
- Validate household member and dietary profile settings persist.
- Validate common-compatible mode filters out meals/options incompatible with active dietary profiles.
- Validate separate-variation mode can select compatible options for different configured diet groups.
- Validate variation-option history affects option scoring independently of parent meal history.
- Validate skipped meals do not count as eaten.
- Validate marking eaten creates a meal event.
- Validate grocery and prep checked state persists for the current weekly plan.
- Validate seed import is idempotent.
- Validate private database files and local seed catalogs are ignored by git.

## Home Assistant Add-on Verification

- Validate `repository.yaml` and `family-menu/config.yaml` are present and contain generic install metadata.
- Build the add-on image locally for `aarch64` using the Home Assistant base image build args.
- Confirm the image starts through `family-menu/run.sh`.
- Confirm `GET /health` returns `ok` inside the container.
- Confirm the Angular UI is served from the container root path.
- Confirm `/data/options.json` can set database path, seed path, host, port, and auto-seed behavior.
- Confirm environment variables override `/data/options.json`.
- Confirm the SQLite database is created under `/data` by default and is not included in git.
- Confirm the add-on build context does not include private databases, private seed catalogs, exports, caches, or `node_modules`.
- Confirm CI runs backend tests, builds the Angular frontend, and validates the add-on image build without publishing.

## Recommendation Verification

- High-likability meals appear more often over repeated simulated weeks than low-likability meals.
- Recently eaten meals are penalized.
- Underused meals are boosted.
- Underused variation options are boosted within an eligible parent meal and dimension.
- Consecutive leftover style repetition is avoided when alternatives exist.
- Manual replacement and lock behavior do not corrupt score history.
- Dietary compatibility filtering does not corrupt meal or option usage history.

## Frontend Verification

- Weekly Plan supports generate, replace meal, swap variation option, reorder, lock, mark eaten, skip, and variation-option changes.
- Weekly Plan shows inline variation label, option, and icon-only lock controls without duplicate variation-summary paragraphs.
- Weekly Plan does not show label chip sets, keeps the meal picker width constrained, and keeps variation rows compact without large label-to-dropdown gaps.
- Weekly Plan keeps the meal picker anchored next to the date block, and selected variation option text is vertically centered in its dropdown field.
- Weekly Plan preserves the last viewed week when navigating away to another screen and back in the same browser session.
- Weekly Plan opens meal instructions in a dialog and exposes source links when configured.
- Meal Catalog supports meal create, edit, archive, restore, search, label/tag filtering below the meal list, source links with open actions, instructions, and likability changes.
- Meal Catalog create flow opens a new editable draft, saves a named meal, selects the created meal read-only, validates missing names, and cancels without creating a row.
- Newly created active meals appear in the Weekly Plan replacement selector after the catalog refreshes.
- Meal Catalog supports variation dimension and variation option create/edit/archive/restore for created meals after the meal itself is saved.
- Grocery and Prep shows aggregated grocery items and prep tasks.
- Grocery and Prep preserves its last viewed week when navigating away and back in the same browser session.
- Weekly Plan and Grocery and Prep remembered weeks are independent from each other.
- Grocery and Prep checkboxes persist across reloads and screen changes.
- History shows meal events and last eaten dates.
- History Add Event has clear spacing between the section header and the Meal dropdown.
- Family Config and Settings changes affect new plans.
- Family Config supports household members, dietary profiles, and mixed-diet mode.

## Manual Verification

- Generate a realistic week from the starter catalog.
- Configure at least two dietary profiles and verify both mixed-diet modes.
- Replace one suggested meal with another.
- Lock two meals and regenerate the rest.
- Lock and unlock an individual variation using the icon-only control.
- Open a planned meal's instructions dialog and source link.
- Select a meal label/tag in Meal Catalog and confirm it filters the list.
- Mark a meal eaten and confirm it appears in History.
- Confirm the next generated week accounts for the eaten meal.
- Confirm grocery and prep output is usable for a Sunday shopping trip.
- Confirm `git status --short` does not include private database, private seed, or exported backup files.
- Scan tracked candidate files for household-specific relationship terms, private diet assignments, and user-specific meal lists before committing.

## Browser Verification

- Test desktop and phone-sized viewports.
- Check that controls and text do not overlap.
- Check that variation controls stay compact and inline on desktop/tablet while collapsing cleanly on phones.
- Check that Weekly Plan variation rows do not have excessive vertical padding or large blank space between label and dropdown.
- Check that Weekly Plan meal picker left edges sit next to the date block and do not drift toward the row center.
- Check that variation dropdown selected-option text is vertically centered.
- Check that navigating to next week, then to Meal Catalog, then back to Weekly Plan keeps next week selected.
- Check that navigating within Grocery and Prep, then away and back, keeps the Grocery and Prep week selected.
- Check that changing the Weekly Plan selected week does not change the remembered Grocery and Prep week, and changing the Grocery and Prep week does not change the remembered Weekly Plan week.
- Check that Meal Catalog label chips sit below the meal list and source URL has a nearby open-link action.
- Check that instruction dialogs fit on desktop and phone-sized viewports.
- Check that the History Add Event header does not crowd the Meal dropdown.
- Check keyboard access for primary controls.
- Check loading, empty, error, and save-failure states where practical.
