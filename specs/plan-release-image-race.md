# Release Image Race Plan

## Goal

Prevent Home Assistant update attempts from failing with `404 manifest unknown` when repository metadata advertises a new Family Menu add-on version before the matching GHCR image tag is available.

## Phase 1: Add Release Image Verification

- Add a small release verification helper that reads `family-menu/config.yaml` and checks `ghcr.io/kmcrandom/family-menu-ha:<version>` with `docker manifest inspect`.
- Allow the helper to accept an explicit version for checking a just-published release.
- Keep the helper read-only; it should not tag, push, publish, or mutate repository files.
- Return a non-zero exit code and a clear message when Docker is unavailable or the manifest does not exist yet.

## Phase 2: Document Release Ordering

- Update repository release documentation to make the race-free order explicit:
  - prepare the version and changelog commit locally;
  - push the `v<version>` tag so GitHub Actions publishes the image;
  - wait for the publish workflow to complete;
  - run the manifest verification helper;
  - only then treat the add-on version as ready for Home Assistant updates.
- Note that if Home Assistant already refreshed during the publish window, retrying the update after the manifest exists should be sufficient.

## Phase 3: Add Focused Tests

- Add tests that confirm the helper reads the add-on image and version from `family-menu/config.yaml`.
- Add tests for override handling and failure messaging without requiring a real GHCR or Docker network call.
- Keep tests local and deterministic by mocking the manifest command.

## Verification

- Run the focused release-helper tests.
- Run `python -m pytest -q` if the focused tests pass.
- Run the helper against the current release image, expecting `ghcr.io/kmcrandom/family-menu-ha:0.1.9` to resolve.

## Risks and Notes

- The helper verifies availability but cannot stop Home Assistant from polling during an in-progress release. The release process must still avoid announcing readiness before the manifest check passes.
- `docker manifest inspect` depends on local Docker CLI availability; tests should not require Docker.
- Changing the actual release order is an operational workflow change, not a Home Assistant runtime or app behavior change.
