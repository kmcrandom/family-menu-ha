# Family Menu Home Assistant Add-on

Family Menu is a local-first weekly dinner planning app with meal variations, grocery lists, prep tasks, history, and household configuration.

## Installation

1. Add this repository to Home Assistant as an add-on repository.
2. Install the **Family Menu** add-on.
3. Start the add-on.
4. Open the app through the Home Assistant sidebar or add-on ingress page.

## Configuration

Default options:

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

The SQLite database is stored under `/data` by default and persists across add-on restarts and upgrades.

The packaged seed catalog is generic sample data. Private meal catalogs, exports, and database backups should stay outside git and should be restored through the app or mounted only in private installations.

## Access

Normal access can use Home Assistant ingress. The add-on also exposes host port `8081` by default so a trusted local reverse proxy can forward to `http://<home-assistant-host>:8081`.

Direct port access should be treated as trusted local-network access only until app-level authentication is added. If the app is reachable from the public internet, protect it with an authenticated reverse proxy, VPN, Home Assistant access layer, or similar control.

## Backup

Back up `/data/family-menu.sqlite` or use the app export endpoint when available. Do not commit database files or private seed catalogs to source control.
