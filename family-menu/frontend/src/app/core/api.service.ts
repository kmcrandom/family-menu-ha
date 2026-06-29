import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import {
  DietaryProfile,
  GroceryPrep,
  GroceryPrepItem,
  HouseholdConfig,
  HouseholdMember,
  ImportDataResponse,
  Meal,
  MealEvent,
  PlannedMeal,
  Preferences,
  VariationDimension,
  VariationOption,
  VacationBlock,
  WeeklyPlan,
} from './models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = this.resolveApiBase();

  apiUrl(path = ''): string {
    const normalized = path.replace(/^\/+/, '');
    return normalized ? `${this.base}/${normalized}` : this.base;
  }

  getMeals(includeArchived = false): Observable<Meal[]> {
    return this.http.get<Meal[]>(this.apiUrl('meals'), {
      params: { include_archived: String(includeArchived) },
    });
  }

  getMeal(id: string): Observable<Meal> {
    return this.http.get<Meal>(this.apiUrl(`meals/${id}`));
  }

  createMeal(payload: Partial<Meal>): Observable<Meal> {
    return this.http.post<Meal>(this.apiUrl('meals'), payload);
  }

  patchMeal(id: string, payload: Partial<Meal>): Observable<Meal> {
    return this.http.patch<Meal>(this.apiUrl(`meals/${id}`), payload);
  }

  archiveMeal(id: string): Observable<Meal> {
    return this.http.post<Meal>(this.apiUrl(`meals/${id}/archive`), {});
  }

  restoreMeal(id: string): Observable<Meal> {
    return this.http.post<Meal>(this.apiUrl(`meals/${id}/restore`), {});
  }

  createOption(dimensionId: string, payload: Partial<VariationOption>): Observable<VariationOption> {
    return this.http.post<VariationOption>(this.apiUrl(`variation-dimensions/${dimensionId}/options`), payload);
  }

  createDimension(mealId: string, payload: Partial<VariationDimension>): Observable<VariationDimension> {
    return this.http.post<VariationDimension>(this.apiUrl(`meals/${mealId}/variation-dimensions`), payload);
  }

  patchOption(id: string, payload: Partial<VariationOption>): Observable<VariationOption> {
    return this.http.patch<VariationOption>(this.apiUrl(`variation-options/${id}`), payload);
  }

  archiveOption(id: string): Observable<VariationOption> {
    return this.http.post<VariationOption>(this.apiUrl(`variation-options/${id}/archive`), {});
  }

  restoreOption(id: string): Observable<VariationOption> {
    return this.http.post<VariationOption>(this.apiUrl(`variation-options/${id}/restore`), {});
  }

  patchDimension(id: string, payload: Partial<VariationDimension>): Observable<VariationDimension> {
    return this.http.patch<VariationDimension>(this.apiUrl(`variation-dimensions/${id}`), payload);
  }

  archiveDimension(id: string): Observable<VariationDimension> {
    return this.http.post<VariationDimension>(this.apiUrl(`variation-dimensions/${id}/archive`), {});
  }

  restoreDimension(id: string): Observable<VariationDimension> {
    return this.http.post<VariationDimension>(this.apiUrl(`variation-dimensions/${id}/restore`), {});
  }

  getCurrentPlan(): Observable<WeeklyPlan> {
    return this.http.get<WeeklyPlan>(this.apiUrl('plans/current'));
  }

  getPlanByWeek(weekStartDate: string): Observable<WeeklyPlan> {
    return this.http.get<WeeklyPlan>(this.apiUrl('plans'), {
      params: { week_start_date: weekStartDate },
    });
  }

  generatePlan(planId: string, payload = {}): Observable<WeeklyPlan> {
    return this.http.post<WeeklyPlan>(this.apiUrl(`plans/${planId}/generate`), payload);
  }

  createVacationBlock(planId: string, payload: Partial<VacationBlock>): Observable<WeeklyPlan> {
    return this.http.post<WeeklyPlan>(this.apiUrl(`plans/${planId}/vacation-blocks`), payload);
  }

  deleteVacationBlock(blockId: string): Observable<WeeklyPlan> {
    return this.http.delete<WeeklyPlan>(this.apiUrl(`vacation-blocks/${blockId}`));
  }

  patchPlannedMeal(id: string, payload: Partial<PlannedMeal>): Observable<PlannedMeal> {
    return this.http.patch<PlannedMeal>(this.apiUrl(`planned-meals/${id}`), payload);
  }

  markEaten(id: string): Observable<MealEvent> {
    return this.http.post<MealEvent>(this.apiUrl(`planned-meals/${id}/mark-eaten`), {});
  }

  skipMeal(id: string): Observable<PlannedMeal> {
    return this.http.post<PlannedMeal>(this.apiUrl(`planned-meals/${id}/skip`), {});
  }

  getGroceryPrep(planId: string): Observable<GroceryPrep> {
    return this.http.get<GroceryPrep>(this.apiUrl(`plans/${planId}/grocery-prep`));
  }

  patchChecklistItem(
    planId: string,
    payload: GroceryPrepItem & { kind: 'grocery' | 'prep' },
  ): Observable<GroceryPrep> {
    return this.http.patch<GroceryPrep>(this.apiUrl(`plans/${planId}/checklist-items`), payload);
  }

  getHistory(): Observable<MealEvent[]> {
    return this.http.get<MealEvent[]>(this.apiUrl('history'));
  }

  createHistory(payload: Partial<MealEvent>): Observable<MealEvent> {
    return this.http.post<MealEvent>(this.apiUrl('history'), payload);
  }

  deleteHistory(id: string): Observable<{ deleted: boolean }> {
    return this.http.delete<{ deleted: boolean }>(this.apiUrl(`history/${id}`));
  }

  getPreferences(): Observable<Preferences> {
    return this.http.get<Preferences>(this.apiUrl('preferences'));
  }

  patchPreferences(payload: Partial<Preferences>): Observable<Preferences> {
    return this.http.patch<Preferences>(this.apiUrl('preferences'), payload);
  }

  getHousehold(): Observable<HouseholdConfig> {
    return this.http.get<HouseholdConfig>(this.apiUrl('household'));
  }

  patchHousehold(payload: Partial<Preferences>): Observable<HouseholdConfig> {
    return this.http.patch<HouseholdConfig>(this.apiUrl('household'), payload);
  }

  createHouseholdMember(payload: Partial<HouseholdMember>): Observable<HouseholdMember> {
    return this.http.post<HouseholdMember>(this.apiUrl('household/members'), payload);
  }

  patchHouseholdMember(id: string, payload: Partial<HouseholdMember>): Observable<HouseholdMember> {
    return this.http.patch<HouseholdMember>(this.apiUrl(`household/members/${id}`), payload);
  }

  createDietaryProfile(payload: Partial<DietaryProfile>): Observable<DietaryProfile> {
    return this.http.post<DietaryProfile>(this.apiUrl('household/dietary-profiles'), payload);
  }

  patchDietaryProfile(id: string, payload: Partial<DietaryProfile>): Observable<DietaryProfile> {
    return this.http.patch<DietaryProfile>(this.apiUrl(`household/dietary-profiles/${id}`), payload);
  }

  importData(data: Record<string, unknown>, confirmOverwrite: boolean): Observable<ImportDataResponse> {
    return this.http.post<ImportDataResponse>(this.apiUrl('import'), {
      data,
      confirm_overwrite: confirmOverwrite,
    });
  }

  private resolveApiBase(): string {
    const baseHref = document.querySelector('base')?.href || window.location.href;
    const path = new URL('api/v1', baseHref).pathname;
    return path.endsWith('/') ? path.slice(0, -1) : path;
  }
}
