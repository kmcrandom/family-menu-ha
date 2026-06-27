import { CommonModule, DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { ApiService } from '../core/api.service';
import { GroceryPrep, GroceryPrepItem, Meal, PlannedMeal, VacationBlock, VariationDimension, VariationOption, WeeklyPlan } from '../core/models';
import { MATERIAL_IMPORTS } from '../shared/material';

interface VacationConfirmData {
  title: string;
  message: string;
}

interface MealInstructionsData {
  item: PlannedMeal;
  optionInstructions: { dimension: string; option: string; instructions: string[] }[];
}

@Component({
  selector: 'app-vacation-confirm-dialog',
  imports: [MATERIAL_IMPORTS],
  template: `
    <h2 mat-dialog-title>{{ data.title }}</h2>
    <mat-dialog-content>
      <p>{{ data.message }}</p>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button type="button" (click)="dialogRef.close(false)">Cancel</button>
      <button mat-flat-button color="warn" type="button" (click)="dialogRef.close(true)">Confirm</button>
    </mat-dialog-actions>
  `,
})
export class VacationConfirmDialogComponent {
  readonly data = inject<VacationConfirmData>(MAT_DIALOG_DATA);
  readonly dialogRef = inject(MatDialogRef<VacationConfirmDialogComponent>);
}

@Component({
  selector: 'app-meal-instructions-dialog',
  imports: [CommonModule, MATERIAL_IMPORTS],
  template: `
    <h2 mat-dialog-title>{{ data.item.meal.name }}</h2>
    <mat-dialog-content class="instructions-dialog">
      @if (data.item.meal.source_url) {
        <a mat-stroked-button [href]="data.item.meal.source_url" target="_blank" rel="noopener noreferrer">
          <mat-icon>open_in_new</mat-icon>
          {{ data.item.meal.source_name || 'Open source' }}
        </a>
      }

      @if (data.item.meal.instructions.length) {
        <section>
          <h3>Meal Instructions</h3>
          <ol>
            @for (step of data.item.meal.instructions; track step) {
              <li>{{ step }}</li>
            }
          </ol>
        </section>
      }

      @for (group of data.optionInstructions; track group.dimension + group.option) {
        <section>
          <h3>{{ group.dimension }}: {{ group.option }}</h3>
          <ol>
            @for (step of group.instructions; track step) {
              <li>{{ step }}</li>
            }
          </ol>
        </section>
      }

      @if (!data.item.meal.instructions.length && !data.optionInstructions.length) {
        <p class="muted">No cooking instructions have been added for this meal yet.</p>
      }
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-flat-button type="button" (click)="dialogRef.close()">Close</button>
    </mat-dialog-actions>
  `,
})
export class MealInstructionsDialogComponent {
  readonly data = inject<MealInstructionsData>(MAT_DIALOG_DATA);
  readonly dialogRef = inject(MatDialogRef<MealInstructionsDialogComponent>);
}

@Component({
  selector: 'app-weekly-plan',
  imports: [CommonModule, DatePipe, FormsModule, MATERIAL_IMPORTS],
  templateUrl: './weekly-plan.component.html',
})
export class WeeklyPlanComponent {
  private readonly rememberedWeekKey = 'family-menu.weekly-plan.week-start';
  private readonly api = inject(ApiService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly dialog = inject(MatDialog);

  plan?: WeeklyPlan;
  meals: Meal[] = [];
  grocery?: GroceryPrep;
  loading = true;
  saving = false;
  error = '';
  currentWeekStartDate = '';
  selectedWeekStartDate = '';

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.api.getMeals().subscribe({
      next: (meals) => {
        this.meals = meals;
        this.api.getCurrentPlan().subscribe({
          next: (plan) => {
            this.currentWeekStartDate = plan.week_start_date;
            const rememberedWeek = this.rememberedWeek();
            if (rememberedWeek && rememberedWeek !== plan.week_start_date) {
              this.loadWeek(rememberedWeek);
              return;
            }
            this.setPlan(plan);
            this.loading = false;
            this.saving = false;
            this.cdr.detectChanges();
          },
          error: () => this.fail('Unable to load the current plan.'),
        });
      },
      error: () => this.fail('Unable to load meals.'),
    });
  }

  loadWeek(weekStartDate: string): void {
    this.loading = true;
    this.error = '';
    this.api.getPlanByWeek(weekStartDate).subscribe({
      next: (plan) => {
        this.setPlan(plan);
        this.loading = false;
        this.saving = false;
        this.cdr.detectChanges();
      },
      error: () => this.fail('Unable to load the selected plan.'),
    });
  }

  previousWeek(): void {
    if (!this.plan || this.loading || this.saving) return;
    this.loadWeek(this.addDays(this.plan.week_start_date, -7));
  }

  nextWeek(): void {
    if (!this.plan || this.loading || this.saving) return;
    this.loadWeek(this.addDays(this.plan.week_start_date, 7));
  }

  currentWeek(): void {
    if (!this.currentWeekStartDate || this.loading || this.saving) return;
    this.loadWeek(this.currentWeekStartDate);
  }

  isCurrentWeek(): boolean {
    return !!this.plan && this.plan.week_start_date === this.currentWeekStartDate;
  }

  generate(): void {
    if (!this.plan || this.isFullWeekVacation()) return;
    this.saving = true;
    this.api.generatePlan(this.plan.id, { preserve_locked: true, regenerate_variations: true }).subscribe({
      next: (plan) => {
        this.plan = this.sortedPlan(plan);
        this.loadGrocery();
        this.saving = false;
        this.cdr.detectChanges();
      },
      error: () => this.fail('Unable to generate suggestions.'),
    });
  }

  toggleVacationWeek(): void {
    if (!this.plan) return;
    const weekBlock = this.fullWeekVacationBlock();
    if (!weekBlock) {
      this.confirmVacation(
        'Mark week as vacation?',
        `Existing planned meals for the week of ${this.plan.week_start_date} will be deleted.`
      ).subscribe((confirmed) => {
        if (confirmed) this.setVacationWeek();
      });
      return;
    }
    this.setVacationWeek();
  }

  private setVacationWeek(): void {
    if (!this.plan) return;
    const weekBlock = this.fullWeekVacationBlock();
    this.saving = true;
    const request = weekBlock
      ? this.api.deleteVacationBlock(weekBlock.id)
      : this.api.createVacationBlock(this.plan.id, {
          start_date: this.plan.week_start_date,
          end_date: this.addDays(this.plan.week_start_date, 6),
          scope: 'week',
          label: 'Vacation',
        });
    request.subscribe({
      next: (plan) => {
        this.setPlan(plan);
        this.saving = false;
        this.cdr.detectChanges();
      },
      error: () => this.fail('Unable to update vacation mode.'),
    });
  }

  toggleVacationDate(date: string): void {
    if (!this.plan) return;
    const block = this.vacationBlockForDate(date);
    if (!block) {
      this.confirmVacation(
        'Mark day as vacation?',
        `Any planned meal on ${date} will be deleted.`
      ).subscribe((confirmed) => {
        if (confirmed) this.setVacationDate(date);
      });
      return;
    }
    this.setVacationDate(date);
  }

  private setVacationDate(date: string): void {
    if (!this.plan) return;
    const block = this.vacationBlockForDate(date);
    this.saving = true;
    const request = block
      ? this.api.deleteVacationBlock(block.id)
      : this.api.createVacationBlock(this.plan.id, {
          start_date: date,
          end_date: date,
          scope: 'day',
          label: 'Vacation',
        });
    request.subscribe({
      next: (plan) => {
        this.setPlan(plan);
        this.saving = false;
        this.cdr.detectChanges();
      },
      error: () => this.fail('Unable to update vacation day.'),
    });
  }

  private confirmVacation(title: string, message: string) {
    return this.dialog
      .open(VacationConfirmDialogComponent, {
        data: { title, message },
        width: '420px',
      })
      .afterClosed();
  }

  visibleDinnerDates(): string[] {
    if (!this.plan) return [];
    return Array.from({ length: this.plan.target_dinner_count }, (_, index) =>
      this.addDays(this.plan!.week_start_date, index + 1),
    );
  }

  isFullWeekVacation(): boolean {
    return !!this.fullWeekVacationBlock();
  }

  vacationBlockForDate(dateValue: string): VacationBlock | undefined {
    if (!this.plan) return undefined;
    return this.plan.vacation_blocks.find((block) => dateValue >= block.start_date && dateValue <= block.end_date);
  }

  isDateBlocked(dateValue: string): boolean {
    return !!this.vacationBlockForDate(dateValue);
  }

  replaceMeal(item: PlannedMeal, mealId: string): void {
    this.patch(item, { meal_id: mealId });
  }

  setVariation(item: PlannedMeal, dimensionId: string, optionId: string): void {
    const next = { ...item.variation_selections, [dimensionId]: optionId };
    this.patch(item, { variation_selections: next });
  }

  toggleMealLock(item: PlannedMeal): void {
    this.patch(item, { locked: !item.locked });
  }

  toggleVariationLock(item: PlannedMeal, dimensionId: string): void {
    const locks = { ...item.variation_locks, [dimensionId]: !item.variation_locks[dimensionId] };
    this.patch(item, { variation_locks: locks });
  }

  showInstructions(item: PlannedMeal): void {
    this.dialog.open(MealInstructionsDialogComponent, {
      data: {
        item,
        optionInstructions: this.selectedOptionInstructions(item),
      },
      width: '560px',
      maxWidth: '94vw',
    });
  }

  markEaten(item: PlannedMeal): void {
    this.saving = true;
    this.api.markEaten(item.id).subscribe({
      next: () => this.reloadSelectedPlan(),
      error: () => this.fail('Unable to mark the meal eaten.'),
    });
  }

  skip(item: PlannedMeal): void {
    this.saving = true;
    this.api.skipMeal(item.id).subscribe({
      next: () => this.reloadSelectedPlan(),
      error: () => this.fail('Unable to skip the meal.'),
    });
  }

  toggleChecklist(kind: 'grocery' | 'prep', item: GroceryPrepItem, event: Event | { checked: boolean }): void {
    if (!this.plan) return;
    const materialEvent = event as { checked?: boolean };
    const input = event instanceof Event ? (event.target as HTMLInputElement | null) : null;
    const checked = materialEvent.checked ?? Boolean(input?.checked);
    item.checked = checked;
    this.api.patchChecklistItem(this.plan.id, { ...item, kind, checked }).subscribe({
      next: (grocery) => {
        this.grocery = grocery;
        this.error = '';
        this.cdr.detectChanges();
      },
      error: () => {
        item.checked = !checked;
        if (input) input.checked = !checked;
        this.fail('Unable to save checklist state.');
      },
    });
  }

  move(item: PlannedMeal, delta: number): void {
    if (!this.plan) return;
    const meals = this.plan.planned_meals;
    const index = meals.findIndex((candidate) => candidate.id === item.id);
    const swap = meals[index + delta];
    if (!swap) return;
    this.saving = true;
    this.api.patchPlannedMeal(item.id, { position: swap.position, planned_date: swap.planned_date }).subscribe({
      next: () => {
        this.api.patchPlannedMeal(swap.id, { position: item.position, planned_date: item.planned_date }).subscribe({
          next: () => this.reloadSelectedPlan(),
          error: () => this.fail('Unable to reorder meals.'),
        });
      },
      error: () => this.fail('Unable to reorder meals.'),
    });
  }

  optionName(item: PlannedMeal, dimension: VariationDimension): string {
    const optionId = item.variation_selections[dimension.id];
    return dimension.options.find((option) => option.id === optionId)?.name ?? 'Choose';
  }

  selectedOptionLabel(item: PlannedMeal): string {
    return item.meal.variation_dimensions
      .map((dimension) => `${dimension.name}: ${this.optionName(item, dimension)}`)
      .join(' / ');
  }

  selectedOptionInstructions(item: PlannedMeal): { dimension: string; option: string; instructions: string[] }[] {
    return item.meal.variation_dimensions
      .map((dimension) => {
        const option = this.selectedOption(item, dimension);
        return option && option.instructions.length
          ? { dimension: dimension.name, option: option.name, instructions: option.instructions }
          : undefined;
      })
      .filter((value): value is { dimension: string; option: string; instructions: string[] } => Boolean(value));
  }

  selectedOption(item: PlannedMeal, dimension: VariationDimension): VariationOption | undefined {
    const optionId = item.variation_selections[dimension.id];
    return dimension.options.find((option) => option.id === optionId);
  }

  variationToneClass(dimension: VariationDimension): string {
    const key = dimension.key.toLowerCase();
    if (key.includes('primary_protein')) return 'variation-tone-primary-protein';
    if (key.includes('diet_protein') || key.includes('pescatarian')) return 'variation-tone-diet-protein';
    if (key.includes('vegetable')) return 'variation-tone-vegetables';
    if (key.includes('sauce')) return 'variation-tone-sauce';
    if (key.includes('starch') || key.includes('base') || key.includes('pasta')) return 'variation-tone-base';
    if (key.includes('topping')) return 'variation-tone-toppings';
    if (key.includes('prep')) return 'variation-tone-prep';
    return 'variation-tone-neutral';
  }

  private patch(item: PlannedMeal, payload: Partial<PlannedMeal>): void {
    this.saving = true;
    this.api.patchPlannedMeal(item.id, payload).subscribe({
      next: () => this.reloadSelectedPlan(),
      error: () => this.fail('Unable to save the meal change.'),
    });
  }

  private reloadSelectedPlan(): void {
    if (!this.selectedWeekStartDate) {
      this.load();
      return;
    }
    this.loadWeek(this.selectedWeekStartDate);
  }

  private setPlan(plan: WeeklyPlan): void {
    this.plan = this.sortedPlan(plan);
    this.selectedWeekStartDate = plan.week_start_date;
    this.rememberWeek(plan.week_start_date);
    this.loadGrocery();
  }

  private rememberedWeek(): string | null {
    try {
      const value = sessionStorage.getItem(this.rememberedWeekKey);
      return value && this.isIsoDate(value) ? value : null;
    } catch {
      return null;
    }
  }

  private rememberWeek(weekStartDate: string): void {
    if (!this.isIsoDate(weekStartDate)) return;
    try {
      sessionStorage.setItem(this.rememberedWeekKey, weekStartDate);
    } catch {
      // Session storage can be unavailable in private or restricted browser modes.
    }
  }

  private isIsoDate(value: string): boolean {
    return /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(`${value}T00:00:00`));
  }

  private loadGrocery(): void {
    if (!this.plan || this.plan.planned_meals.length === 0) {
      this.grocery = undefined;
      return;
    }
    this.api.getGroceryPrep(this.plan.id).subscribe({
      next: (grocery) => {
        this.grocery = grocery;
        this.cdr.detectChanges();
      },
      error: () => {
        this.grocery = undefined;
        this.cdr.detectChanges();
      },
    });
  }

  private sortedPlan(plan: WeeklyPlan): WeeklyPlan {
    return {
      ...plan,
      vacation_blocks: [...(plan.vacation_blocks ?? [])].sort((a, b) => a.start_date.localeCompare(b.start_date)),
      planned_meals: [...plan.planned_meals].sort((a, b) => a.position - b.position),
    };
  }

  private fullWeekVacationBlock(): VacationBlock | undefined {
    return this.plan?.vacation_blocks.find((block) => block.scope === 'week');
  }

  private addDays(isoDate: string, days: number): string {
    const [year, month, day] = isoDate.split('-').map((part) => Number(part));
    const date = new Date(year, month - 1, day);
    date.setDate(date.getDate() + days);
    return this.formatDate(date);
  }

  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private fail(message: string): void {
    this.error = message;
    this.loading = false;
    this.saving = false;
    this.cdr.detectChanges();
  }
}
