# Plan: Vacation Mode

## Goal

Support whole-week and specific-day vacation blocks so no meals are planned on blocked dates. If meals already exist on those dates, adding the vacation block removes them.

## Implementation Steps

1. Backend schema and models
   - Add a `vacation_blocks` table with `weekly_plan_id`, `start_date`, `end_date`, `scope`, `label`, `created_at`, and `updated_at`.
   - Add Pydantic schemas for vacation block read/create/patch payloads.
   - Add `vacation_blocks` to `WeeklyPlan` responses.
   - Keep migration backward-compatible for existing `family-menu.db`.

2. Backend store and API
   - Add store methods to list, create, patch, and delete vacation blocks.
   - When creating or patching a block, delete planned meals for the affected dates.
   - Add API endpoints:
     - `POST /api/v1/plans/{plan_id}/vacation-blocks`
     - `PATCH /api/v1/vacation-blocks/{block_id}`
     - `DELETE /api/v1/vacation-blocks/{block_id}`
   - Return the updated weekly plan from vacation block mutations so the UI can refresh in one call.

3. Recommendation behavior
   - Teach `generate_plan` to compute blocked dates from the selected plan's vacation blocks.
   - Skip blocked dates when selecting meals.
   - Delete unlocked planned meals on blocked dates during regeneration.
   - Preserve locked meals only if they are not on blocked dates; vacation is a hard constraint.
   - If all five dinner dates are blocked, generation returns a plan with no planned meals.

4. Frontend API and models
   - Add `VacationBlock` type and vacation block API methods.
   - Include `vacation_blocks` on `WeeklyPlan`.

5. Weekly Plan UI
   - Add a compact vacation toolbar near week navigation:
     - `Vacation Week` / `End Vacation Week`.
     - Per-planned-day `Vacation` action.
   - Show blocked dates when a partial-week vacation exists.
   - Show a full-week vacation empty state and hide/disable Generate while the whole week is blocked.
   - Refresh the selected week after creating or deleting vacation blocks.

6. Tests and verification
   - Add backend tests for:
     - full-week vacation removes existing meals and generation produces zero meals.
     - day vacation removes that day's meal and generation skips that date.
     - deleting a vacation block does not auto-generate meals.
   - Run the full backend test suite.
   - Build Angular.
   - Browser-smoke-test:
     - Generate or open a week with meals.
     - Mark one date vacation and confirm that meal disappears and the blocked date is shown.
     - Mark the whole week vacation and confirm all meals disappear and Generate is disabled/hidden.
     - Remove vacation mode and confirm meals are not auto-created until Generate is clicked.

## Risks

- Existing locked meals on vacation dates could conflict with user expectations. The spec treats vacation as a hard constraint, so those meals should be removed too.
- Position numbering may have gaps when some days are blocked. The UI should continue sorting by `position` and showing actual `planned_date`; generation can keep original weekday positions for clarity.
- Grocery and prep checklists are derived from planned meals, so removing meals should naturally remove their generated items. Existing checked checklist rows may remain in storage but should not appear if no matching meal ingredients are generated.

## Non-Goals

- Recurring vacations.
- Multi-week vacation creation in one action.
- Travel meal planning, restaurant planning, or pantry mode.
- Calendar picker UI beyond whole-week and visible-day controls.
