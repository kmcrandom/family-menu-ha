# Home Assistant Add-on Implementation Plan

## Goal

Prepare Family Menu to install and run as a Home Assistant add-on while preserving local development, tests, generic sample data, and private-data git hygiene.

## Phase 1: Restructure Runnable Source Into Add-on Context

- Create the installable add-on folder `family-menu/`.
- Move the Python package from `family_menu/src/family_menu/` to `family-menu/src/family_menu/`.
- Move Angular frontend source from `frontend/` to `family-menu/frontend/`.
- Move generic public seed data from `data/generic-starter-meal-catalog.example.json` to `family-menu/data/generic-starter-meal-catalog.example.json`.
- Keep specs, tests, root README, root `pyproject.toml`, and repository metadata at the repo root.
- Update `pyproject.toml`, pytest config, docs, tests, and Angular output paths for the new source locations.
- Preserve ignored private files in place:
  - `family-menu.db`
  - `data/starter-meal-catalog.json`
  - `backups/`
  - virtualenvs, caches, build output, and `node_modules/`

## Phase 2: Add Home Assistant Repository and Add-on Files

- Add root `repository.yaml` with generic Family Menu repository metadata.
- Add `family-menu/config.yaml` with:
  - `name: Family Menu`
  - `slug: family_menu`
  - `version: "0.1.0"`
  - `image: ghcr.io/kmcrandom/family-menu-ha`
  - `arch: [aarch64]`
  - ingress enabled on port `8097`
  - optional direct `8097/tcp` mapping
  - options and schema for database path, seed path, auto-seed, host, and port
- Add `family-menu/Dockerfile` based on `ghcr.io/home-assistant/${BUILD_ARCH}-base:latest`.
- Add `family-menu/run.sh` that launches `python3 -m family_menu`.
- Add `family-menu/requirements.txt` for runtime dependencies.
- Add `family-menu/.dockerignore` excluding private databases, private seed files, exports, caches, build output, and `node_modules`.
- Add `family-menu/README.md` with install, configuration, data location, ingress, and local-network access notes.

## Phase 3: Add Home Assistant Runtime Options

- Update `family_menu.config.load_settings()` to read `/data/options.json` when present.
- Support add-on options:
  - `database.path`
  - `seed.path`
  - `seed.auto_seed`
  - `server.host`
  - `server.port`
- Keep environment variables as the highest-precedence overrides:
  - `FAMILY_MENU_DB`
  - `FAMILY_MENU_SEED`
  - `FAMILY_MENU_STATIC`
  - `FAMILY_MENU_HOST`
  - `FAMILY_MENU_PORT`
  - `FAMILY_MENU_RELOAD`
  - `FAMILY_MENU_AUTO_SEED`
- Default local development to repo-local paths.
- Default add-on runtime to:
  - database: `/data/family-menu.sqlite`
  - seed: `/app/data/generic-starter-meal-catalog.example.json`
  - static: `/app/src/family_menu/static`
  - host/port: `0.0.0.0:8097`
- Add tests for options-file parsing, default add-on paths, and environment override precedence.

## Phase 4: CI and Publish Workflow

- Add `.github/workflows/ci.yml` with jobs for:
  - Python tests.
  - Angular production build.
  - Home Assistant add-on image build validation for `linux/arm64` without publishing.
- Add `.github/workflows/publish-home-assistant-addon.yml` triggered by `v*` tags and manual dispatch.
- Publish tags:
  - `ghcr.io/kmcrandom/family-menu-ha:<version>`
  - `ghcr.io/kmcrandom/family-menu-ha:latest`
- Read the add-on version from `family-menu/config.yaml`.

## Phase 5: Documentation and Git Hygiene

- Update root `README.md` for the new repo layout and add-on install path.
- Update `.gitignore` for the moved frontend/build/static paths and private local data.
- Add or update general project docs as needed so users know:
  - local database location
  - Home Assistant database location
  - how generic seed data works
  - private catalogs must stay ignored
- Run a privacy scan before commit for household-specific names, relationship terms, private diet assignments, and user-specific meal lists.

## Verification

- `python -m pytest -q`
- `cd family-menu/frontend && npm install` if dependencies are missing, then `npm run build`
- `python -m family_menu` local smoke check if practical
- `curl /health` against the local app if a smoke server is started
- `docker buildx build --platform linux/arm64 --build-arg BUILD_ARCH=aarch64 --build-arg BUILD_VERSION=0.1.0 family-menu`
- Confirm add-on build context excludes ignored private files.
- Confirm `git status --short --ignored` shows private DB, private seed, backups, `node_modules`, caches, and built static files as ignored only.

## Risks and Notes

- Moving the frontend and backend source will create a large but mechanical diff.
- Local virtualenv editable installs may need reinstalling after the package path changes.
- Existing local private DB can stay in the repo root for development because `FAMILY_MENU_DB` still supports explicit overrides; new default local paths should be documented.
- Docker `buildx` may require local Docker Desktop/QEMU support; if unavailable, CI workflow syntax and local app tests still provide partial verification.
- The add-on will rely on Home Assistant ingress for normal access. Direct port access should remain local-network only until app-level authentication is added.

