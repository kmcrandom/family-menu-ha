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
  private readonly base = '/api/v1';

  getMeals(includeArchived = false): Observable<Meal[]> {
    return this.http.get<Meal[]>(`${this.base}/meals`, {
      params: { include_archived: String(includeArchived) },
    });
  }

  getMeal(id: string): Observable<Meal> {
    return this.http.get<Meal>(`${this.base}/meals/${id}`);
  }

  patchMeal(id: string, payload: Partial<Meal>): Observable<Meal> {
    return this.http.patch<Meal>(`${this.base}/meals/${id}`, payload);
  }

  archiveMeal(id: string): Observable<Meal> {
    return this.http.post<Meal>(`${this.base}/meals/${id}/archive`, {});
  }

  restoreMeal(id: string): Observable<Meal> {
    return this.http.post<Meal>(`${this.base}/meals/${id}/restore`, {});
  }

  createOption(dimensionId: string, payload: Partial<VariationOption>): Observable<VariationOption> {
    return this.http.post<VariationOption>(`${this.base}/variation-dimensions/${dimensionId}/options`, payload);
  }

  patchOption(id: string, payload: Partial<VariationOption>): Observable<VariationOption> {
    return this.http.patch<VariationOption>(`${this.base}/variation-options/${id}`, payload);
  }

  archiveOption(id: string): Observable<VariationOption> {
    return this.http.post<VariationOption>(`${this.base}/variation-options/${id}/archive`, {});
  }

  restoreOption(id: string): Observable<VariationOption> {
    return this.http.post<VariationOption>(`${this.base}/variation-options/${id}/restore`, {});
  }

  patchDimension(id: string, payload: Partial<VariationDimension>): Observable<VariationDimension> {
    return this.http.patch<VariationDimension>(`${this.base}/variation-dimensions/${id}`, payload);
  }

  getCurrentPlan(): Observable<WeeklyPlan> {
    return this.http.get<WeeklyPlan>(`${this.base}/plans/current`);
  }

  getPlanByWeek(weekStartDate: string): Observable<WeeklyPlan> {
    return this.http.get<WeeklyPlan>(`${this.base}/plans`, {
      params: { week_start_date: weekStartDate },
    });
  }

  generatePlan(planId: string, payload = {}): Observable<WeeklyPlan> {
    return this.http.post<WeeklyPlan>(`${this.base}/plans/${planId}/generate`, payload);
  }

  createVacationBlock(planId: string, payload: Partial<VacationBlock>): Observable<WeeklyPlan> {
    return this.http.post<WeeklyPlan>(`${this.base}/plans/${planId}/vacation-blocks`, payload);
  }

  deleteVacationBlock(blockId: string): Observable<WeeklyPlan> {
    return this.http.delete<WeeklyPlan>(`${this.base}/vacation-blocks/${blockId}`);
  }

  patchPlannedMeal(id: string, payload: Partial<PlannedMeal>): Observable<PlannedMeal> {
    return this.http.patch<PlannedMeal>(`${this.base}/planned-meals/${id}`, payload);
  }

  markEaten(id: string): Observable<MealEvent> {
    return this.http.post<MealEvent>(`${this.base}/planned-meals/${id}/mark-eaten`, {});
  }

  skipMeal(id: string): Observable<PlannedMeal> {
    return this.http.post<PlannedMeal>(`${this.base}/planned-meals/${id}/skip`, {});
  }

  getGroceryPrep(planId: string): Observable<GroceryPrep> {
    return this.http.get<GroceryPrep>(`${this.base}/plans/${planId}/grocery-prep`);
  }

  patchChecklistItem(
    planId: string,
    payload: GroceryPrepItem & { kind: 'grocery' | 'prep' },
  ): Observable<GroceryPrep> {
    return this.http.patch<GroceryPrep>(`${this.base}/plans/${planId}/checklist-items`, payload);
  }

  getHistory(): Observable<MealEvent[]> {
    return this.http.get<MealEvent[]>(`${this.base}/history`);
  }

  createHistory(payload: Partial<MealEvent>): Observable<MealEvent> {
    return this.http.post<MealEvent>(`${this.base}/history`, payload);
  }

  deleteHistory(id: string): Observable<{ deleted: boolean }> {
    return this.http.delete<{ deleted: boolean }>(`${this.base}/history/${id}`);
  }

  getPreferences(): Observable<Preferences> {
    return this.http.get<Preferences>(`${this.base}/preferences`);
  }

  patchPreferences(payload: Partial<Preferences>): Observable<Preferences> {
    return this.http.patch<Preferences>(`${this.base}/preferences`, payload);
  }

  getHousehold(): Observable<HouseholdConfig> {
    return this.http.get<HouseholdConfig>(`${this.base}/household`);
  }

  patchHousehold(payload: Partial<Preferences>): Observable<HouseholdConfig> {
    return this.http.patch<HouseholdConfig>(`${this.base}/household`, payload);
  }

  createHouseholdMember(payload: Partial<HouseholdMember>): Observable<HouseholdMember> {
    return this.http.post<HouseholdMember>(`${this.base}/household/members`, payload);
  }

  patchHouseholdMember(id: string, payload: Partial<HouseholdMember>): Observable<HouseholdMember> {
    return this.http.patch<HouseholdMember>(`${this.base}/household/members/${id}`, payload);
  }

  createDietaryProfile(payload: Partial<DietaryProfile>): Observable<DietaryProfile> {
    return this.http.post<DietaryProfile>(`${this.base}/household/dietary-profiles`, payload);
  }

  patchDietaryProfile(id: string, payload: Partial<DietaryProfile>): Observable<DietaryProfile> {
    return this.http.patch<DietaryProfile>(`${this.base}/household/dietary-profiles/${id}`, payload);
  }

  importData(data: Record<string, unknown>, confirmOverwrite: boolean): Observable<ImportDataResponse> {
    return this.http.post<ImportDataResponse>(`${this.base}/import`, {
      data,
      confirm_overwrite: confirmOverwrite,
    });
  }
}
