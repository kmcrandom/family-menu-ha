# Deployment and Packaging

## Initial Deployment

The first version should run as a standalone local web app:

- FastAPI service.
- SQLite database.
- Static browser UI served by the app.
- Local development command.
- Optional Dockerfile once the app shape stabilizes.

## Home Assistant Add-on Packaging

Family Menu should be packaged as a Home Assistant add-on repository using the same broad shape as the local MinuteMetrics Home Assistant repository:

```text
repository.yaml
family-menu/
  config.yaml
  Dockerfile
  run.sh
  README.md
  requirements.txt
  .dockerignore
  src/
  frontend/
```

Home Assistant add-on Docker builds use the add-on directory as the Docker build context. Because of that, the runnable backend and frontend source needed by the image must live inside the add-on folder, not only in repo-root sibling folders. The preferred packaging change is to make `family-menu/` the installable add-on folder and move the runnable Python package, Angular app, and public seed data into that folder, then update local development and tests to use the new paths.

The root of the repository should contain Home Assistant repository metadata and project-level files:

- `repository.yaml` with generic repository metadata.
- `.github/workflows/ci.yml` for backend tests, frontend build, and add-on image build validation.
- `.github/workflows/publish-home-assistant-addon.yml` for tagged GHCR image publishing.
- Project docs, specs, security/contribution docs, and tests.

The add-on metadata should include:

- `name: Family Menu`
- `slug: family_menu`
- `version` matching the package release version.
- `image: ghcr.io/kmcrandom/family-menu-ha`
- `arch` initially containing `aarch64`.
- `startup: application`
- `boot: auto`
- `init: false`
- `ingress: true`
- `ingress_port: 8081`
- `panel_title: Family Menu`
- `panel_icon: mdi:food-variant`
- `stage: experimental`
- Optional direct port mapping for local-network access to the same FastAPI/Angular UI.

The add-on Dockerfile should follow the MinuteMetrics pattern:

- Base image: `ghcr.io/home-assistant/${BUILD_ARCH}-base:latest`.
- Build args: `BUILD_ARCH` and `BUILD_VERSION`.
- Install Python and Node/npm build dependencies.
- Build the Angular frontend during the image build.
- Install Python runtime dependencies into a virtual environment.
- Copy the generic seed data into the image.
- Launch through `/run.sh`.
- Set `FAMILY_MENU_HOST=0.0.0.0`, `FAMILY_MENU_PORT=8081`, and a default static path inside the image.

Published installs should pull a pre-built GHCR image rather than compiling on the Home Assistant device. Local development builds remain possible by removing the `image` field from a copied local add-on config and letting Supervisor build the Dockerfile.

## Home Assistant Runtime

The app should be structured so it can later be packaged as a Home Assistant add-on:

- Configurable data directory.
- Configurable host and port.
- No dependency on native OS paths.
- Static UI served by the same backend.
- Ingress-friendly routing.
- Health endpoint.

Runtime configuration should support both environment variables and Home Assistant add-on options:

- Environment variables remain available for local development and tests.
- In the add-on, `/data/options.json` should be read when present.
- Environment variables override add-on options so development and test harnesses can force paths.
- Default add-on database path: `/data/family-menu.sqlite`.
- Default add-on seed path: packaged generic sample data, unless `seed.path` is configured.
- Default add-on static path: built Angular static assets inside the image.
- Default host/port: `0.0.0.0:8081` in the add-on, `127.0.0.1:8081` for local development.
- Optional `auto_seed` setting controls whether an empty database imports the seed catalog.

Example add-on options:

```yaml
database:
  path: /data/family-menu.sqlite
seed:
  path: /app/data/generic-starter-meal-catalog.example.json
  auto_seed: true
server:
  host: 0.0.0.0
  port: 8081
```

The schema should validate these options as strings/booleans/ports without requiring any household-specific values.

## Cloud Position

Cloud hosting is not part of the initial scope. AWS or another cloud platform may be considered later only if the household needs access independent of home network access, managed backups, shared external access, or uptime beyond a local server.

## Backup and Portability

- SQLite is the source of truth.
- Export should produce a portable JSON backup.
- Import and merge restore should be added after the first local app pass.
- The app should document where the database lives in local and Home Assistant deployments.
- Default development database location is repo-local, such as `family-menu.db`, but all SQLite database files should be ignored by git.
- Private seed catalogs and exported backups should be ignored by git by default.
- Public sample data must be sanitized and generic before being tracked.

## Git Hygiene

- Ignore `*.db`, `family-menu.db`, local seed catalogs, and app exports.
- Keep only generic sample seed data in git, preferably using an `.example.json` suffix.
- Before commit, run a repo scan for household-specific names, relationship terms, private diet assignments, and user-specific meal lists.
- Source files and specs should describe generic household configuration instead of the installing user's real household.

## Security Expectations

- Local development may run without authentication.
- If the app is exposed beyond localhost or Home Assistant ingress, it should require authentication or be placed behind a trusted access layer.
- The add-on should rely on Home Assistant ingress for normal in-Home Assistant access.
- Direct port access should be treated as local-network access and documented accordingly until first-class app authentication exists.
- No secrets should be committed.
- No private household composition, diet assignments, real meal history, or user-specific catalog should be committed.
- No telemetry should be enabled by default.

## Acceptance Criteria

- The app can run locally without Home Assistant.
- The app is installable as a Home Assistant add-on repository entry.
- The add-on image can be built locally for `aarch64`.
- Published installs can pull `ghcr.io/kmcrandom/family-menu-ha:<version>` and `latest`.
- The add-on starts from a clean install, serves the Angular UI through ingress, and reports `GET /health` as healthy.
- Data persists under `/data` across add-on restarts.
- The database path can be configured for local development, Docker, and Home Assistant add-on storage.
- `/data/options.json` settings are honored when present, and environment variables still override them.
- A clean commit can be created without staging private database, private seed, or exported backup files.
