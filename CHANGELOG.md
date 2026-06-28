# Changelog

## 0.1.8 - 2026-06-28

- Add controlled randomness when regenerating unlocked meals and variation options.
- Keep regeneration bounded to high-scoring eligible candidates while preserving locks, vacation blocks, duplicate prevention, and dietary compatibility.

## 0.1.7 - 2026-06-28

- Move the Meal Catalog Add variation entry point under the current variation dimensions.
- Keep variation type, name, key, and color controls hidden until Add variation is activated.
- Replace inline existing-variation color palettes with a color dropper icon that opens a color selection popup.

## 0.1.6 - 2026-06-28

- Move Meal Catalog Archive/Edit and Save/Cancel actions into the selected meal header.
- Confirm meal archive actions before archiving and remove the duplicate Source URL field icon.
- Add edit-mode variation dimension add/remove controls with reusable type suggestions.
- Add custom variation types with Material color presets and custom color selection.
- Preserve variation dimension colors through API responses, migrations, import/export, Meal Catalog, and Weekly Plan.

## 0.1.5 - 2026-06-27

- Add a Home Assistant add-on changelog inside the add-on folder.
- Add release validation so the add-on config version must have a matching changelog entry.
- Open existing Meal Catalog meals read-only by default and require Edit before making changes.
- Add Save and Cancel edit-mode controls for Meal Catalog meal details.
- Keep Meal Catalog variation and archive actions disabled until edit mode is active.

## 0.1.4 - 2026-06-27

- Move Meal Catalog label filtering into the search bar so phone layouts no longer cut off label chips.
- Add a compact filter menu for selecting labels and a clearable active-label indicator.
- Align the Meal Catalog list with the editor on wider screens.
- Ignore macOS `.DS_Store` metadata files.

## 0.1.3 - 2026-06-27

- Fix Home Assistant sidebar ingress path handling so the UI can load under generated ingress subpaths.
- Keep direct root access working for trusted reverse proxy hostnames.
- Add tests for prefixed ingress API, static asset, and SPA route handling.

## 0.1.2 - 2026-06-27

- Add full-overwrite JSON import/restore from Family Menu exports.
- Add Family Config import/export controls with restore confirmation and import summary.
- Restore validates data before replacing existing app data and rolls back failed imports.

## 0.1.1 - 2026-06-27

- Add the Family Menu favicon.
- Expose the Home Assistant add-on on port 8081.

## 0.1.0 - 2026-06-27

- Initial Home Assistant add-on release.
