from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


Status = Literal["active", "archived"]
PlanStatus = Literal["draft", "planned", "completed", "archived"]
PlannedMealState = Literal["planned", "eaten", "skipped", "moved"]
MixedDietMode = Literal["separate_variations", "common_compatible_only"]
DietaryProfileType = Literal["omnivore", "vegetarian", "vegan", "pescatarian", "no_pork", "no_beef", "custom"]
VacationScope = Literal["day", "week"]


class IngredientItem(BaseModel):
    label: str
    amount: str | None = None
    unit: str | None = None
    category: str | None = None
    note: str | None = None

    @field_validator("label", mode="before")
    @classmethod
    def label_text(cls, value: Any) -> str:
        return str(value or "").strip()

    @field_validator("amount", "unit", "category", "note", mode="before")
    @classmethod
    def optional_text(cls, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


def normalize_ingredient_items(value: Any) -> list[dict[str, str | None]]:
    if value is None:
        return []
    items: list[dict[str, str | None]] = []
    for item in value:
        if isinstance(item, str):
            payload: dict[str, Any] = {"label": item}
        elif isinstance(item, dict):
            payload = item
        else:
            payload = {"label": str(item)}
        ingredient = IngredientItem(**payload)
        if ingredient.label:
            items.append(ingredient.model_dump(exclude_none=True))
    return items


class IngredientListMixin(BaseModel):
    @field_validator("shared_ingredients", "ingredient_additions", check_fields=False, mode="before")
    @classmethod
    def ingredient_list(cls, value: Any) -> list[dict[str, str | None]]:
        return normalize_ingredient_items(value)


class HealthResponse(BaseModel):
    status: str
    version: str


class VariationOption(IngredientListMixin):
    id: str
    dimension_id: str
    meal_id: str
    name: str
    status: Status = "active"
    likability: int = Field(default=80, ge=0, le=100)
    value: dict[str, Any] | list[str] = Field(default_factory=dict)
    diet_tags: list[str] = Field(default_factory=list)
    compatible_diet_profiles: list[str] = Field(default_factory=list)
    ingredient_additions: list[IngredientItem] = Field(default_factory=list)
    ingredient_omissions: list[str] = Field(default_factory=list)
    prep_ahead: list[str] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    overrides: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class VariationDimension(BaseModel):
    id: str
    meal_id: str
    key: str
    name: str
    selection_mode: str = "single"
    required: bool = False
    display_order: int = 0
    status: Status = "active"
    options: list[VariationOption] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Meal(IngredientListMixin):
    id: str
    name: str
    status: Status = "active"
    likability: int = Field(default=80, ge=0, le=100)
    active_prep_minutes: int = Field(default=20, ge=0)
    cook_minutes: int = Field(default=20, ge=0)
    make_ahead_score: int = Field(default=50, ge=0, le=100)
    leftover_quality: int = Field(default=70, ge=0, le=100)
    leftover_style: str = "mixed"
    tags: list[str] = Field(default_factory=list)
    diet_tags: list[str] = Field(default_factory=list)
    shared_ingredients: list[IngredientItem] = Field(default_factory=list)
    primary_proteins: list[str] = Field(default_factory=list)
    alternate_proteins: list[str] = Field(default_factory=list)
    prep_ahead: list[str] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    source_url: str | None = None
    source_name: str | None = None
    simple_serving_variations: list[str] = Field(default_factory=list)
    notes: str | None = None
    variation_dimensions: list[VariationDimension] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MealPatch(IngredientListMixin):
    name: str | None = None
    status: Status | None = None
    likability: int | None = Field(default=None, ge=0, le=100)
    active_prep_minutes: int | None = Field(default=None, ge=0)
    cook_minutes: int | None = Field(default=None, ge=0)
    make_ahead_score: int | None = Field(default=None, ge=0, le=100)
    leftover_quality: int | None = Field(default=None, ge=0, le=100)
    leftover_style: str | None = None
    tags: list[str] | None = None
    diet_tags: list[str] | None = None
    shared_ingredients: list[IngredientItem] | None = None
    primary_proteins: list[str] | None = None
    alternate_proteins: list[str] | None = None
    prep_ahead: list[str] | None = None
    instructions: list[str] | None = None
    source_url: str | None = None
    source_name: str | None = None
    simple_serving_variations: list[str] | None = None
    notes: str | None = None


class VariationDimensionCreate(BaseModel):
    key: str
    name: str
    selection_mode: str = "single"
    required: bool = False
    display_order: int = 0


class VariationDimensionPatch(BaseModel):
    key: str | None = None
    name: str | None = None
    selection_mode: str | None = None
    required: bool | None = None
    display_order: int | None = None
    status: Status | None = None


class VariationOptionCreate(IngredientListMixin):
    name: str
    likability: int = Field(default=80, ge=0, le=100)
    value: dict[str, Any] | list[str] = Field(default_factory=dict)
    diet_tags: list[str] = Field(default_factory=list)
    compatible_diet_profiles: list[str] = Field(default_factory=list)
    ingredient_additions: list[IngredientItem] = Field(default_factory=list)
    ingredient_omissions: list[str] = Field(default_factory=list)
    prep_ahead: list[str] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    overrides: dict[str, Any] = Field(default_factory=dict)


class VariationOptionPatch(IngredientListMixin):
    name: str | None = None
    status: Status | None = None
    likability: int | None = Field(default=None, ge=0, le=100)
    value: dict[str, Any] | list[str] | None = None
    diet_tags: list[str] | None = None
    compatible_diet_profiles: list[str] | None = None
    ingredient_additions: list[IngredientItem] | None = None
    ingredient_omissions: list[str] | None = None
    prep_ahead: list[str] | None = None
    instructions: list[str] | None = None
    tags: list[str] | None = None
    overrides: dict[str, Any] | None = None


class Preferences(BaseModel):
    household_name: str = "Family Menu"
    mixed_diet_mode: MixedDietMode = "separate_variations"
    week_start_day: str = "Sunday"
    shopping_day: str = "Sunday"
    default_week_size: int = Field(default=5, ge=1, le=14)
    default_dinner_servings: int = Field(default=4, ge=1)
    default_leftover_lunch_servings: int = Field(default=2, ge=0)
    max_same_meal_per_week: int = Field(default=1, ge=1)
    soft_repeat_gap_days: int = Field(default=14, ge=0)
    avoid_consecutive_leftover_styles: bool = True
    recommendation_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "likability": 0.34,
            "frequency": 0.24,
            "recency": 0.20,
            "prep": 0.12,
            "leftovers": 0.10,
        }
    )
    variation_recency_weight: float = 0.45
    variation_frequency_weight: float = 0.35


class HouseholdMember(BaseModel):
    id: str
    display_name: str
    status: Status = "active"
    dinner_servings: float = Field(default=1, ge=0)
    leftover_lunch_servings: float = Field(default=0, ge=0)
    dietary_profile_ids: list[str] = Field(default_factory=list)
    preference_tags: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class HouseholdMemberCreate(BaseModel):
    display_name: str
    dinner_servings: float = Field(default=1, ge=0)
    leftover_lunch_servings: float = Field(default=0, ge=0)
    dietary_profile_ids: list[str] = Field(default_factory=list)
    preference_tags: list[str] = Field(default_factory=list)


class HouseholdMemberPatch(BaseModel):
    display_name: str | None = None
    status: Status | None = None
    dinner_servings: float | None = Field(default=None, ge=0)
    leftover_lunch_servings: float | None = Field(default=None, ge=0)
    dietary_profile_ids: list[str] | None = None
    preference_tags: list[str] | None = None


class DietaryProfile(BaseModel):
    id: str
    name: str
    type: DietaryProfileType = "custom"
    excluded_tags: list[str] = Field(default_factory=list)
    included_tags: list[str] = Field(default_factory=list)
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DietaryProfileCreate(BaseModel):
    name: str
    type: DietaryProfileType = "custom"
    excluded_tags: list[str] = Field(default_factory=list)
    included_tags: list[str] = Field(default_factory=list)
    notes: str | None = None


class DietaryProfilePatch(BaseModel):
    name: str | None = None
    type: DietaryProfileType | None = None
    excluded_tags: list[str] | None = None
    included_tags: list[str] | None = None
    notes: str | None = None


class HouseholdPatch(BaseModel):
    household_name: str | None = None
    mixed_diet_mode: MixedDietMode | None = None


class HouseholdConfig(BaseModel):
    preferences: Preferences
    members: list[HouseholdMember] = Field(default_factory=list)
    dietary_profiles: list[DietaryProfile] = Field(default_factory=list)
    database_path: str | None = None
    seed_path: str | None = None


class WeeklyPlan(BaseModel):
    id: str
    week_start_date: date
    shopping_date: date
    target_dinner_count: int
    status: PlanStatus
    notes: str | None = None
    vacation_blocks: list["VacationBlock"] = Field(default_factory=list)
    planned_meals: list["PlannedMeal"] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class VacationBlock(BaseModel):
    id: str
    weekly_plan_id: str
    start_date: date
    end_date: date
    scope: VacationScope = "day"
    label: str = "Vacation"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class VacationBlockCreate(BaseModel):
    start_date: date
    end_date: date | None = None
    scope: VacationScope = "day"
    label: str = "Vacation"


class VacationBlockPatch(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    scope: VacationScope | None = None
    label: str | None = None


class PlannedMeal(BaseModel):
    id: str
    weekly_plan_id: str
    meal_id: str
    meal: Meal | None = None
    variation_selections: dict[str, str] = Field(default_factory=dict)
    planned_date: date
    position: int
    meal_slot: str = "dinner"
    servings_dinner: int = 4
    leftover_lunch_servings: int = 2
    locked: bool = False
    variation_locks: dict[str, bool] = Field(default_factory=dict)
    state: PlannedMealState = "planned"
    notes: str | None = None
    recommendation_reasons: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PlannedMealPatch(BaseModel):
    meal_id: str | None = None
    variation_selections: dict[str, str] | None = None
    planned_date: date | None = None
    position: int | None = None
    locked: bool | None = None
    variation_locks: dict[str, bool] | None = None
    state: PlannedMealState | None = None
    notes: str | None = None


class GeneratePlanRequest(BaseModel):
    preserve_locked: bool = True
    regenerate_variations: bool = True


class MealEvent(BaseModel):
    id: str
    meal_id: str
    meal: Meal | None = None
    planned_meal_id: str | None = None
    eaten_date: date
    variation_selections: dict[str, str] = Field(default_factory=dict)
    servings_dinner: int = 4
    leftover_lunch_servings: int = 2
    feedback: Literal["liked", "neutral", "disliked"] | None = None
    notes: str | None = None
    created_at: datetime | None = None


class MealEventCreate(BaseModel):
    meal_id: str
    planned_meal_id: str | None = None
    eaten_date: date
    variation_selections: dict[str, str] = Field(default_factory=dict)
    servings_dinner: int = 4
    leftover_lunch_servings: int = 2
    feedback: Literal["liked", "neutral", "disliked"] | None = None
    notes: str | None = None


class GroceryPrepItem(BaseModel):
    id: str | None = None
    kind: Literal["grocery", "prep"] | None = None
    label: str
    category: str = "General"
    source: str
    amount: str | None = None
    unit: str | None = None
    amount_display: str | None = None
    amount_details: list[str] = Field(default_factory=list)
    checked: bool = False


class ChecklistItemPatch(BaseModel):
    kind: Literal["grocery", "prep"]
    label: str
    category: str = "General"
    source: str = ""
    checked: bool = False


class GroceryPrepResponse(BaseModel):
    plan_id: str
    grocery_items: list[GroceryPrepItem]
    prep_items: list[GroceryPrepItem]


class ImportDataRequest(BaseModel):
    data: dict[str, Any]
    confirm_overwrite: bool = False


class ImportDataResponse(BaseModel):
    imported: dict[str, int]
    household: HouseholdConfig


WeeklyPlan.model_rebuild()
