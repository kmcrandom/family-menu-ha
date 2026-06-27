# Deployment and Packaging

## Initial Deployment

The first version should run as a standalone local web app:

- FastAPI service.
- SQLite database.
- Static browser UI served by the app.
- Local development command.
- Optional Dockerfile once the app shape stabilizes.

## Home Assistant Path

The app should be structured so it can later be packaged as a Home Assistant add-on:

- Configurable data directory.
- Configurable host and port.
- No dependency on native OS paths.
- Static UI served by the same backend.
- Ingress-friendly routing.
- Health endpoint.

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
- No secrets should be committed.
- No private household composition, diet assignments, real meal history, or user-specific catalog should be committed.
- No telemetry should be enabled by default.

## Acceptance Criteria

- The app can run locally without Home Assistant.
- The app can later be packaged for Home Assistant without replacing the backend architecture.
- The database path can be configured for local development, Docker, and Home Assistant add-on storage.
- A clean commit can be created without staging private database, private seed, or exported backup files.
