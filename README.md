# Family Menu

Family Menu is a local-first weekly dinner planning web app for a household that wants configurable serving counts, dietary profiles, shared-base meals, grocery shopping, prep-ahead tasks, and meal suggestions that learn from eating history.

The initial direction is a standalone FastAPI and SQLite web app that can later be packaged for Home Assistant. There is no native iOS app in the initial scope.

## Local Development

Create a Python environment and install the backend:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
```

Install and build the Angular frontend:

```bash
cd family-menu/frontend
npm install
npm run build
cd ../..
```

Run the local app:

```bash
.venv/bin/python -m family_menu
```

The app serves the built Angular UI at `http://127.0.0.1:8097` and seeds generic sample meals into `family-menu.db` on first run. Override runtime paths with environment variables such as `FAMILY_MENU_DB`, `FAMILY_MENU_SEED`, `FAMILY_MENU_STATIC`, `FAMILY_MENU_HOST`, and `FAMILY_MENU_PORT`.

## Home Assistant Add-on

This repository is structured as a Home Assistant add-on repository. Add the repository URL in Home Assistant, install the **Family Menu** add-on, then open it through the sidebar or ingress page.

The installable add-on lives in `family-menu/` and includes:

- `config.yaml`
- `Dockerfile`
- `run.sh`
- `requirements.txt`
- Python backend source under `src/`
- Angular frontend source under `frontend/`
- generic sample seed data under `data/`

The add-on stores its SQLite database at `/data/family-menu.sqlite` by default. Published installs pull `ghcr.io/kmcrandom/family-menu-ha:<version>`.

## Private Data

The default local database is `family-menu.db` in the repo root. It is ignored by git, along with `*.db`, private seed catalogs, and exports.

Tracked source uses `family-menu/data/generic-starter-meal-catalog.example.json` as public sample data. Put real household catalogs in ignored local files such as `data/starter-meal-catalog.json` or `family-menu/data/starter-meal-catalog.json` and point the app at them with `FAMILY_MENU_SEED` when needed.

Run backend verification:

```bash
.venv/bin/python -m pytest -q
```

## Specification Set

- [Product Requirements](specs/product-requirements.md)
- [System Architecture](specs/system-architecture.md)
- [API and Data Model](specs/api-data-model.md)
- [Recommendation Engine](specs/recommendation-engine.md)
- [Web App Overview](specs/web-app.md)
- [Weekly Plan Screen](specs/screen-weekly-plan.md)
- [Meal Catalog Screen](specs/screen-meal-catalog.md)
- [Grocery and Prep Screen](specs/screen-grocery-prep.md)
- [History Screen](specs/screen-history.md)
- [Settings Screen](specs/screen-settings.md)
- [Starter Meal Catalog](specs/starter-meal-catalog.md)
- [Deployment and Packaging](specs/deployment-packaging.md)
- [Verification Plan](specs/verification.md)
- [Delivery Roadmap](specs/delivery-roadmap.md)
- [Initial Web App Implementation Plan](specs/plan-initial-webapp.md)
- [Privacy and Generic Family Config Plan](specs/plan-privacy-generic-config.md)
