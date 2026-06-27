import { CommonModule, DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { Meal, MealEvent } from '../core/models';
import { MATERIAL_IMPORTS } from '../shared/material';

@Component({
  selector: 'app-history',
  imports: [CommonModule, DatePipe, FormsModule, MATERIAL_IMPORTS],
  templateUrl: './history.component.html',
})
export class HistoryComponent {
  private readonly api = inject(ApiService);
  private readonly cdr = inject(ChangeDetectorRef);

  events: MealEvent[] = [];
  meals: Meal[] = [];
  selectedMealId = '';
  eatenDate = new Date().toISOString().slice(0, 10);
  error = '';

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.api.getMeals().subscribe({
      next: (meals) => {
        this.meals = meals;
        this.selectedMealId ||= meals[0]?.id ?? '';
        this.api.getHistory().subscribe({
          next: (events) => {
            this.events = events;
            this.cdr.detectChanges();
          },
          error: () => {
            this.error = 'Unable to load history.';
            this.cdr.detectChanges();
          },
        });
      },
      error: () => {
        this.error = 'Unable to load meals.';
        this.cdr.detectChanges();
      },
    });
  }

  addEvent(): void {
    const meal = this.meals.find((candidate) => candidate.id === this.selectedMealId);
    if (!meal) return;
    const variation_selections = Object.fromEntries(
      meal.variation_dimensions
        .filter((dimension) => dimension.options.length)
        .map((dimension) => [dimension.id, dimension.options[0].id])
    );
    this.api.createHistory({
      meal_id: meal.id,
      eaten_date: this.eatenDate,
      variation_selections,
      servings_dinner: 4,
      leftover_lunch_servings: 2,
    }).subscribe({
      next: () => this.load(),
      error: () => {
        this.error = 'Unable to add history event.';
        this.cdr.detectChanges();
      },
    });
  }

  deleteEvent(event: MealEvent): void {
    this.api.deleteHistory(event.id).subscribe({
      next: () => this.load(),
      error: () => {
        this.error = 'Unable to delete history event.';
        this.cdr.detectChanges();
      },
    });
  }

  selectedOptions(event: MealEvent): string {
    return event.meal.variation_dimensions
      .map((dimension) => {
        const option = dimension.options.find((candidate) => candidate.id === event.variation_selections[dimension.id]);
        return option ? `${dimension.name}: ${option.name}` : '';
      })
      .filter(Boolean)
      .join(' / ');
  }
}
