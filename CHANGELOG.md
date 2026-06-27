# Changelog

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
