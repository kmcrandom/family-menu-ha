# Delivery Roadmap

## Spec-Driven Development Workflow

Each meaningful change should follow the SDD workflow:

1. Update the relevant specs.
2. Pause for explicit spec approval.
3. Create or update the implementation plan.
4. Pause for explicit plan approval.
5. Implement.
6. Verify.
7. Update specs if implementation reveals a gap.

This document is a product-level delivery roadmap, not the approval-gated implementation plan. The initial implementation plan lives in [Initial Web App Implementation Plan](plan-initial-webapp.md).

## Milestone 1: Specification and Generic Starter Data

Deliverables:

- Product requirements.
- System architecture.
- Data model and API contract.
- Meal and variation-option recommendation behavior.
- Screen specs.
- Generic starter meal catalog definition.
- Private local catalog and database git-ignore rules.
- Deployment direction.
- Verification plan.

Exit criteria:

- The app can be planned without unresolved core product ambiguity.
- The first implementation plan can be written from the specs.

## Milestone 2: Backend Foundation

Deliverables:

- FastAPI app shell.
- SQLite schema and migrations.
- Meal catalog CRUD.
- Generic starter catalog import.
- Private local seed import path.
- Preferences storage.
- Household member and dietary profile storage.

Exit criteria:

- The generic starter catalog can be imported.
- Private local catalogs and databases are not staged for git.
- Meals can be listed, edited, archived, and restored.
- Tests cover schema and catalog behavior.

## Milestone 3: Recommendation and Weekly Plans

Deliverables:

- Weekly plan model.
- Planned meal model.
- Meal event model.
- Variation dimension and option tracking model.
- Recommendation service.
- Plan generation endpoint.
- Mark eaten, skip, lock, replace, and reorder behavior.

Exit criteria:

- A five-meal plan can be generated.
- Locked meals survive regeneration.
- Eating history changes future suggestions.
- Variation-option history changes future option suggestions.
- Tests cover recommendation constraints and scoring behavior.

## Milestone 4: Weekly Plan UI

Deliverables:

- Default app route.
- Generate and regenerate controls.
- Manual replacement and locking.
- Variation-dimension selection.
- Mark eaten and skip.

Exit criteria:

- The core weekly planning workflow is usable in a browser.
- Desktop and phone-sized layouts are functional.

## Milestone 5: Meal Catalog UI

Deliverables:

- Catalog list and detail/edit views.
- Likability editing.
- Protein, variation-dimension, and variation-option editing.
- Archive and restore.
- Search and filters.

Exit criteria:

- The user can maintain the catalog without editing JSON manually.

## Milestone 6: Grocery, Prep, History, and Family Config

Deliverables:

- Grocery and prep aggregation.
- Checklist state for a weekly plan.
- History view.
- Family Config and Settings view.
- Export and import.

Exit criteria:

- The app supports the full Sunday-to-weekday planning loop.

## Milestone 7: Packaging

Deliverables:

- Dockerfile.
- Persistent data configuration.
- Health endpoint.
- Home Assistant add-on packaging if desired.
- Setup and backup documentation.

Exit criteria:

- The app can run reliably on the intended always-on local host.
