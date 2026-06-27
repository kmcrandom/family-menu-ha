export interface IngredientItem {
  label: string;
  amount?: string | null;
  unit?: string | null;
  category?: string | null;
  note?: string | null;
}

export type IngredientValue = IngredientItem | string;

export interface VariationOption {
  id: string;
  dimension_id: string;
  meal_id: string;
  name: string;
  status: 'active' | 'archived';
  likability: number;
  value: Record<string, unknown> | string[];
  diet_tags: string[];
  compatible_diet_profiles: string[];
  ingredient_additions: IngredientValue[];
  ingredient_omissions: string[];
  prep_ahead: string[];
  instructions: string[];
  tags: string[];
  overrides: Record<string, unknown>;
}

export interface VariationDimension {
  id: string;
  meal_id: string;
  key: string;
  name: string;
  selection_mode: string;
  required: boolean;
  display_order: number;
  status: 'active' | 'archived';
  options: VariationOption[];
}

export interface Meal {
  id: string;
  name: string;
  status: 'active' | 'archived';
  likability: number;
  active_prep_minutes: number;
  cook_minutes: number;
  make_ahead_score: number;
  leftover_quality: number;
  leftover_style: string;
  tags: string[];
  diet_tags: string[];
  shared_ingredients: IngredientValue[];
  primary_proteins: string[];
  alternate_proteins: string[];
  prep_ahead: string[];
  instructions: string[];
  source_url?: string | null;
  source_name?: string | null;
  simple_serving_variations: string[];
  notes?: string | null;
  variation_dimensions: VariationDimension[];
}

export interface PlannedMeal {
  id: string;
  weekly_plan_id: string;
  meal_id: string;
  meal: Meal;
  variation_selections: Record<string, string>;
  planned_date: string;
  position: number;
  meal_slot: string;
  servings_dinner: number;
  leftover_lunch_servings: number;
  locked: boolean;
  variation_locks: Record<string, boolean>;
  state: 'planned' | 'eaten' | 'skipped' | 'moved';
  notes?: string | null;
  recommendation_reasons: string[];
}

export interface WeeklyPlan {
  id: string;
  week_start_date: string;
  shopping_date: string;
  target_dinner_count: number;
  status: 'draft' | 'planned' | 'completed' | 'archived';
  notes?: string | null;
  vacation_blocks: VacationBlock[];
  planned_meals: PlannedMeal[];
}

export interface VacationBlock {
  id: string;
  weekly_plan_id: string;
  start_date: string;
  end_date: string;
  scope: 'day' | 'week';
  label: string;
}

export interface MealEvent {
  id: string;
  meal_id: string;
  meal: Meal;
  planned_meal_id?: string | null;
  eaten_date: string;
  variation_selections: Record<string, string>;
  servings_dinner: number;
  leftover_lunch_servings: number;
  feedback?: 'liked' | 'neutral' | 'disliked' | null;
  notes?: string | null;
}

export interface Preferences {
  household_name: string;
  mixed_diet_mode: 'separate_variations' | 'common_compatible_only';
  week_start_day: string;
  shopping_day: string;
  default_week_size: number;
  default_dinner_servings: number;
  default_leftover_lunch_servings: number;
  max_same_meal_per_week: number;
  soft_repeat_gap_days: number;
  avoid_consecutive_leftover_styles: boolean;
  recommendation_weights: Record<string, number>;
  variation_recency_weight: number;
  variation_frequency_weight: number;
}

export interface HouseholdMember {
  id: string;
  display_name: string;
  status: 'active' | 'archived';
  dinner_servings: number;
  leftover_lunch_servings: number;
  dietary_profile_ids: string[];
  preference_tags: string[];
}

export interface DietaryProfile {
  id: string;
  name: string;
  type: 'omnivore' | 'vegetarian' | 'vegan' | 'pescatarian' | 'no_pork' | 'no_beef' | 'custom';
  excluded_tags: string[];
  included_tags: string[];
  notes?: string | null;
}

export interface HouseholdConfig {
  preferences: Preferences;
  members: HouseholdMember[];
  dietary_profiles: DietaryProfile[];
  database_path?: string | null;
  seed_path?: string | null;
}

export interface GroceryPrepItem {
  id?: string;
  kind?: 'grocery' | 'prep';
  label: string;
  category: string;
  source: string;
  amount?: string | null;
  unit?: string | null;
  amount_display?: string | null;
  amount_details?: string[];
  checked: boolean;
}

export interface GroceryPrep {
  plan_id: string;
  grocery_items: GroceryPrepItem[];
  prep_items: GroceryPrepItem[];
}

export interface ImportDataResponse {
  imported: Record<string, number>;
  household: HouseholdConfig;
}
