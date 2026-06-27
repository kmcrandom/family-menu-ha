import { CommonModule, DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { ApiService } from '../core/api.service';
import { GroceryPrep, GroceryPrepItem, WeeklyPlan } from '../core/models';
import { MATERIAL_IMPORTS } from '../shared/material';

@Component({
  selector: 'app-grocery-prep',
  imports: [CommonModule, DatePipe, MATERIAL_IMPORTS],
  templateUrl: './grocery-prep.component.html',
})
export class GroceryPrepComponent {
  private readonly rememberedWeekKey = 'family-menu.grocery-prep.week-start';
  private readonly api = inject(ApiService);
  private readonly cdr = inject(ChangeDetectorRef);

  plan?: WeeklyPlan;
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
    this.api.getCurrentPlan().subscribe({
      next: (plan) => {
        this.currentWeekStartDate = plan.week_start_date;
        this.loadWeek(this.rememberedWeek() ?? this.nextUpcomingSunday());
      },
      error: () => {
        this.error = 'Unable to load grocery and prep.';
        this.loading = false;
        this.cdr.detectChanges();
      },
    });
  }

  loadWeek(weekStartDate: string): void {
    this.loading = true;
    this.error = '';
    this.grocery = undefined;
    this.api.getPlanByWeek(weekStartDate).subscribe({
      next: (plan) => {
        this.setPlan(plan);
        this.loadGrocery();
      },
      error: () => {
        this.error = 'Unable to load the selected grocery and prep week.';
        this.loading = false;
        this.cdr.detectChanges();
      },
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

  nextUpcomingWeek(): void {
    if (!this.currentWeekStartDate || this.loading || this.saving) return;
    this.loadWeek(this.nextUpcomingSunday());
  }

  isNextUpcomingWeek(): boolean {
    return !!this.plan && this.plan.week_start_date === this.nextUpcomingSunday();
  }

  grouped(items: GroceryPrepItem[] = []): [string, GroceryPrepItem[]][] {
    const groups = new Map<string, GroceryPrepItem[]>();
    for (const item of items) {
      groups.set(item.category, [...(groups.get(item.category) ?? []), item]);
    }
    return [...groups.entries()].sort(([a], [b]) => a.localeCompare(b));
  }

  toggleItem(kind: 'grocery' | 'prep', item: GroceryPrepItem, event: Event | { checked: boolean }): void {
    if (!this.plan) return;
    const materialEvent = event as { checked?: boolean };
    const input = event instanceof Event ? (event.target as HTMLInputElement | null) : null;
    const checked = materialEvent.checked ?? Boolean(input?.checked);
    item.checked = checked;
    this.saving = true;
    this.api.patchChecklistItem(this.plan.id, { ...item, kind, checked }).subscribe({
      next: (grocery) => {
        this.grocery = grocery;
        this.error = '';
        this.saving = false;
        this.cdr.detectChanges();
      },
      error: () => {
        item.checked = !checked;
        if (input) input.checked = !checked;
        this.error = 'Unable to save checklist state.';
        this.saving = false;
        this.cdr.detectChanges();
      },
    });
  }

  private setPlan(plan: WeeklyPlan): void {
    this.plan = plan;
    this.selectedWeekStartDate = plan.week_start_date;
    this.rememberWeek(plan.week_start_date);
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

  private loadGrocery(): void {
    if (!this.plan) return;
    this.api.getGroceryPrep(this.plan.id).subscribe({
      next: (grocery) => {
        this.grocery = grocery;
        this.error = '';
        this.loading = false;
        this.saving = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Unable to load grocery and prep for the selected week.';
        this.loading = false;
        this.saving = false;
        this.cdr.detectChanges();
      },
    });
  }

  private nextUpcomingSunday(): string {
    const today = new Date();
    const daysUntilSunday = (7 - today.getDay()) % 7;
    const sunday = new Date(today);
    sunday.setDate(today.getDate() + daysUntilSunday);
    return this.formatDate(sunday);
  }

  private addDays(isoDate: string, days: number): string {
    const [year, month, day] = isoDate.split('-').map(Number);
    const next = new Date(year, month - 1, day);
    next.setDate(next.getDate() + days);
    return this.formatDate(next);
  }

  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private isIsoDate(value: string): boolean {
    return /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(`${value}T00:00:00`));
  }
}
