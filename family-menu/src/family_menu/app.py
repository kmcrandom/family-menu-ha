from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import Settings, load_settings
from .db import connect, init_db
from .recommender import generate_plan
from .schemas import (
    ChecklistItemPatch,
    DietaryProfileCreate,
    DietaryProfilePatch,
    GeneratePlanRequest,
    HealthResponse,
    HouseholdMemberCreate,
    HouseholdMemberPatch,
    HouseholdPatch,
    ImportDataRequest,
    MealEventCreate,
    MealCreate,
    MealPatch,
    PlannedMealPatch,
    VacationBlockCreate,
    VacationBlockPatch,
    VariationDimensionCreate,
    VariationDimensionPatch,
    VariationOptionCreate,
    VariationOptionPatch,
)
from .store import Store


def create_app(settings: Settings | None = None, conn: sqlite3.Connection | None = None) -> FastAPI:
    settings = settings or load_settings()
    db_conn = conn or connect(settings.db_path)
    init_db(db_conn)
    store = Store(db_conn)
    if settings.auto_seed and store.meal_count() == 0 and settings.seed_path.exists():
        store.import_seed(settings.seed_path)

    app = FastAPI(title="Family Menu", version=__version__)
    app.state.store = store
    app.state.settings = settings

    @app.middleware("http")
    async def ingress_prefix_middleware(request, call_next):
        path = request.scope.get("path", "")
        api_marker = "/api/v1"
        if not path.startswith(api_marker) and api_marker in path:
            request.scope["path"] = path[path.index(api_marker) :]
        return await call_next(request)

    @app.get("/health", response_model=HealthResponse)
    def health() -> dict:
        return {"status": "ok", "version": __version__}

    @app.get("/api/v1/meals")
    def list_meals(include_archived: bool = False) -> list[dict]:
        return store.list_meals(include_archived=include_archived)

    @app.get("/api/v1/meals/{meal_id}")
    def get_meal(meal_id: str) -> dict:
        return guard(lambda: store.meal_response(meal_id), meal_id)

    @app.post("/api/v1/meals", status_code=status.HTTP_201_CREATED)
    def create_meal(payload: MealCreate) -> dict:
        return guard(lambda: store.create_meal(payload), payload.name)

    @app.patch("/api/v1/meals/{meal_id}")
    def patch_meal(meal_id: str, payload: MealPatch) -> dict:
        return guard(lambda: store.patch_meal(meal_id, payload), meal_id)

    @app.post("/api/v1/meals/{meal_id}/archive")
    def archive_meal(meal_id: str) -> dict:
        return guard(lambda: store.set_meal_status(meal_id, "archived"), meal_id)

    @app.post("/api/v1/meals/{meal_id}/restore")
    def restore_meal(meal_id: str) -> dict:
        return guard(lambda: store.set_meal_status(meal_id, "active"), meal_id)

    @app.get("/api/v1/meals/{meal_id}/variation-dimensions")
    def list_variation_dimensions(meal_id: str, include_archived: bool = True) -> list[dict]:
        return guard(lambda: store.list_dimensions(meal_id, include_archived=include_archived), meal_id)

    @app.post("/api/v1/meals/{meal_id}/variation-dimensions", status_code=status.HTTP_201_CREATED)
    def create_variation_dimension(meal_id: str, payload: VariationDimensionCreate) -> dict:
        return guard(lambda: store.create_dimension(meal_id, payload), meal_id)

    @app.patch("/api/v1/variation-dimensions/{dimension_id}")
    def patch_variation_dimension(dimension_id: str, payload: VariationDimensionPatch) -> dict:
        return guard(lambda: store.patch_dimension(dimension_id, payload), dimension_id)

    @app.post("/api/v1/variation-dimensions/{dimension_id}/archive")
    def archive_variation_dimension(dimension_id: str) -> dict:
        return guard(lambda: store.patch_dimension(dimension_id, VariationDimensionPatch(status="archived")), dimension_id)

    @app.post("/api/v1/variation-dimensions/{dimension_id}/restore")
    def restore_variation_dimension(dimension_id: str) -> dict:
        return guard(lambda: store.patch_dimension(dimension_id, VariationDimensionPatch(status="active")), dimension_id)

    @app.post("/api/v1/variation-dimensions/{dimension_id}/options", status_code=status.HTTP_201_CREATED)
    def create_variation_option(dimension_id: str, payload: VariationOptionCreate) -> dict:
        return guard(lambda: store.create_option(dimension_id, payload), dimension_id)

    @app.patch("/api/v1/variation-options/{option_id}")
    def patch_variation_option(option_id: str, payload: VariationOptionPatch) -> dict:
        return guard(lambda: store.patch_option(option_id, payload), option_id)

    @app.post("/api/v1/variation-options/{option_id}/archive")
    def archive_variation_option(option_id: str) -> dict:
        return guard(lambda: store.set_option_status(option_id, "archived"), option_id)

    @app.post("/api/v1/variation-options/{option_id}/restore")
    def restore_variation_option(option_id: str) -> dict:
        return guard(lambda: store.set_option_status(option_id, "active"), option_id)

    @app.get("/api/v1/preferences")
    def get_preferences() -> dict:
        return store.get_preferences()

    @app.patch("/api/v1/preferences")
    def patch_preferences(payload: dict) -> dict:
        return store.patch_preferences(payload)

    @app.get("/api/v1/household")
    def get_household() -> dict:
        return store.household_config(str(settings.db_path), str(settings.seed_path))

    @app.patch("/api/v1/household")
    def patch_household(payload: HouseholdPatch) -> dict:
        store.patch_household(payload)
        return store.household_config(str(settings.db_path), str(settings.seed_path))

    @app.post("/api/v1/household/members", status_code=status.HTTP_201_CREATED)
    def create_household_member(payload: HouseholdMemberCreate) -> dict:
        return store.create_household_member(payload)

    @app.patch("/api/v1/household/members/{member_id}")
    def patch_household_member(member_id: str, payload: HouseholdMemberPatch) -> dict:
        return guard(lambda: store.patch_household_member(member_id, payload), member_id)

    @app.post("/api/v1/household/dietary-profiles", status_code=status.HTTP_201_CREATED)
    def create_dietary_profile(payload: DietaryProfileCreate) -> dict:
        return store.create_dietary_profile(payload)

    @app.patch("/api/v1/household/dietary-profiles/{profile_id}")
    def patch_dietary_profile(profile_id: str, payload: DietaryProfilePatch) -> dict:
        return guard(lambda: store.patch_dietary_profile(profile_id, payload), profile_id)

    @app.get("/api/v1/plans/current")
    def current_plan() -> dict:
        return store.get_or_create_plan()

    @app.get("/api/v1/plans")
    def get_plan(week_start_date: date = Query()) -> dict:
        plan = store.get_plan_by_week(week_start_date)
        return plan or store.get_or_create_plan(week_start_date)

    @app.post("/api/v1/plans")
    def create_plan(week_start_date: date | None = None) -> dict:
        return store.get_or_create_plan(week_start_date)

    @app.post("/api/v1/plans/{plan_id}/generate")
    def generate_week(plan_id: str, payload: GeneratePlanRequest = GeneratePlanRequest()) -> dict:
        return guard(
            lambda: generate_plan(
                store,
                plan_id,
                preserve_locked=payload.preserve_locked,
                regenerate_variations=payload.regenerate_variations,
            ),
            plan_id,
        )

    @app.post("/api/v1/plans/{plan_id}/vacation-blocks", status_code=status.HTTP_201_CREATED)
    def create_vacation_block(plan_id: str, payload: VacationBlockCreate) -> dict:
        return guard(lambda: store.create_vacation_block(plan_id, payload), plan_id)

    @app.patch("/api/v1/vacation-blocks/{block_id}")
    def patch_vacation_block(block_id: str, payload: VacationBlockPatch) -> dict:
        return guard(lambda: store.patch_vacation_block(block_id, payload), block_id)

    @app.delete("/api/v1/vacation-blocks/{block_id}")
    def delete_vacation_block(block_id: str) -> dict:
        return guard(lambda: store.delete_vacation_block(block_id), block_id)

    @app.patch("/api/v1/planned-meals/{planned_meal_id}")
    def patch_planned_meal(planned_meal_id: str, payload: PlannedMealPatch) -> dict:
        return guard(lambda: store.patch_planned_meal(planned_meal_id, payload), planned_meal_id)

    @app.post("/api/v1/planned-meals/{planned_meal_id}/mark-eaten")
    def mark_eaten(planned_meal_id: str, feedback: str | None = None) -> dict:
        return guard(lambda: store.create_event_from_planned(planned_meal_id, feedback=feedback), planned_meal_id)

    @app.post("/api/v1/planned-meals/{planned_meal_id}/skip")
    def skip_planned_meal(planned_meal_id: str) -> dict:
        return guard(lambda: store.patch_planned_meal(planned_meal_id, PlannedMealPatch(state="skipped")), planned_meal_id)

    @app.get("/api/v1/plans/{plan_id}/grocery-prep")
    def grocery_prep(plan_id: str) -> dict:
        return guard(lambda: store.grocery_prep(plan_id), plan_id)

    @app.patch("/api/v1/plans/{plan_id}/checklist-items")
    def patch_checklist_item(plan_id: str, payload: ChecklistItemPatch) -> dict:
        return guard(lambda: store.update_checklist_item(plan_id, payload), plan_id)

    @app.get("/api/v1/history")
    def history(limit: int = 200) -> list[dict]:
        return store.list_events(limit=limit)

    @app.post("/api/v1/history", status_code=status.HTTP_201_CREATED)
    def create_history_event(payload: MealEventCreate) -> dict:
        return guard(lambda: store.create_event(payload), payload.meal_id)

    @app.delete("/api/v1/history/{event_id}")
    def delete_history_event(event_id: str) -> dict:
        return guard(lambda: (store.delete_event(event_id), {"deleted": True})[1], event_id)

    @app.get("/api/v1/export")
    def export_data() -> dict:
        return store.export_data()

    @app.post("/api/v1/import")
    def import_data(payload: ImportDataRequest) -> dict:
        try:
            return store.import_data(payload.data, confirm_overwrite=payload.confirm_overwrite)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    mount_frontend(app, settings.static_dir)
    return app


def guard(fn, key: str):
    try:
        return fn()
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found: {key}") from None
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None


def mount_frontend(app: FastAPI, static_dir: Path) -> None:
    static_dir.mkdir(parents=True, exist_ok=True)
    served_dir = static_dir / "browser" if (static_dir / "browser" / "index.html").exists() else static_dir
    assets_dir = served_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    index = served_dir / "index.html"

    @app.get("/", include_in_schema=False)
    def root():
        if index.exists():
            return FileResponse(index)
        return HTMLResponse(
            "<main style='font-family: system-ui; padding: 2rem'>"
            "<h1>Family Menu</h1>"
            "<p>Backend is running. Build the Angular frontend to enable the app UI.</p>"
            "</main>"
        )

    @app.get("/{path:path}", include_in_schema=False)
    def spa_fallback(path: str):
        if path.startswith("api/v1") or path == "health":
            raise HTTPException(status_code=404)
        candidate = safe_static_file(served_dir, path)
        if candidate is not None:
            return FileResponse(candidate)
        if assets_dir.exists() and "/assets/" in f"/{path}":
            asset_path = f"/{path}".split("/assets/", 1)[1]
            asset = safe_static_file(assets_dir, asset_path)
            if asset is not None:
                return FileResponse(asset)
        file_name = Path(path).name
        if file_name:
            prefixed_asset = safe_static_file(served_dir, file_name)
            if prefixed_asset is not None:
                return FileResponse(prefixed_asset)
        if index.exists():
            return FileResponse(index)
        raise HTTPException(status_code=404)


def safe_static_file(base_dir: Path, relative_path: str) -> Path | None:
    candidate = (base_dir / relative_path.lstrip("/")).resolve()
    try:
        candidate.relative_to(base_dir.resolve())
    except ValueError:
        return None
    if candidate.exists() and candidate.is_file():
        return candidate
    return None
