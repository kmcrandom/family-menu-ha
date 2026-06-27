import { Routes } from '@angular/router';
import { WeeklyPlanComponent } from './weekly-plan/weekly-plan.component';
import { MealCatalogComponent } from './meal-catalog/meal-catalog.component';
import { GroceryPrepComponent } from './grocery-prep/grocery-prep.component';
import { HistoryComponent } from './history/history.component';
import { SettingsComponent } from './settings/settings.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'weekly-plan' },
  { path: 'weekly-plan', component: WeeklyPlanComponent },
  { path: 'meal-catalog', component: MealCatalogComponent },
  { path: 'grocery-prep', component: GroceryPrepComponent },
  { path: 'history', component: HistoryComponent },
  { path: 'settings', component: SettingsComponent },
];
