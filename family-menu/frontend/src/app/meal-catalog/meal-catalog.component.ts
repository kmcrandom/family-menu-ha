import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { IngredientItem, IngredientValue, Meal, VariationDimension, VariationOption } from '../core/models';
import { MATERIAL_IMPORTS } from '../shared/material';

@Component({
  selector: 'app-meal-catalog',
  imports: [CommonModule, FormsModule, ReactiveFormsModule, MATERIAL_IMPORTS],
  templateUrl: './meal-catalog.component.html',
})
export class MealCatalogComponent {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);
  private readonly cdr = inject(ChangeDetectorRef);

  meals: Meal[] = [];
  selected?: Meal;
  query = '';
  showArchived = false;
  selectedTag = '';
  error = '';
  saving = false;
  isEditing = false;
  newOptionNames: Record<string, string> = {};

  readonly mealForm = this.fb.group({
    name: [''],
    likability: [80],
    active_prep_minutes: [20],
    cook_minutes: [20],
    make_ahead_score: [50],
    leftover_quality: [70],
    leftover_style: ['mixed'],
    source_url: [''],
    source_name: [''],
    tags_text: [''],
    shared_ingredients_text: [''],
    prep_ahead_text: [''],
    instructions_text: [''],
    notes: [''],
  });

  ngOnInit(): void {
    this.load();
  }

  get filteredMeals(): Meal[] {
    const q = this.query.trim().toLowerCase();
    return this.meals.filter((meal) => {
      if (!this.showArchived && meal.status === 'archived') return false;
      if (this.selectedTag && !meal.tags.includes(this.selectedTag)) return false;
      if (!q) return true;
      const haystack = [
        meal.name,
        meal.leftover_style,
        ...meal.tags,
        ...meal.shared_ingredients.map((ingredient) => this.ingredientLabel(ingredient)),
        ...meal.variation_dimensions.flatMap((dimension) => [
          dimension.name,
          ...dimension.options.map((option) => option.name),
        ]),
      ].join(' ').toLowerCase();
      return haystack.includes(q);
    });
  }

  get availableTags(): string[] {
    const tags = new Set<string>();
    for (const meal of this.meals) {
      if (!this.showArchived && meal.status === 'archived') continue;
      for (const tag of meal.tags) {
        if (tag.trim()) tags.add(tag.trim());
      }
    }
    return [...tags].sort((a, b) => a.localeCompare(b));
  }

  load(selectId?: string, editAfterLoad = false): void {
    this.api.getMeals(true).subscribe({
      next: (meals) => {
        this.meals = meals;
        const next = meals.find((meal) => meal.id === (selectId ?? this.selected?.id)) ?? meals[0];
        if (next) this.selectMeal(next, editAfterLoad);
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Unable to load the meal catalog.';
        this.cdr.detectChanges();
      },
    });
  }

  selectMeal(meal: Meal, editMode = false): void {
    this.selected = meal;
    this.isEditing = editMode;
    this.mealForm.patchValue({
      name: meal.name,
      likability: meal.likability,
      active_prep_minutes: meal.active_prep_minutes,
      cook_minutes: meal.cook_minutes,
      make_ahead_score: meal.make_ahead_score,
      leftover_quality: meal.leftover_quality,
      leftover_style: meal.leftover_style,
      source_url: meal.source_url ?? '',
      source_name: meal.source_name ?? '',
      tags_text: this.tagsToText(meal.tags),
      shared_ingredients_text: this.ingredientsToText(meal.shared_ingredients),
      prep_ahead_text: this.linesToText(meal.prep_ahead),
      instructions_text: this.linesToText(meal.instructions),
      notes: meal.notes ?? '',
    });
    this.syncFormMode();
  }

  startEditing(): void {
    if (!this.selected) return;
    this.isEditing = true;
    this.syncFormMode();
  }

  cancelEditing(): void {
    if (!this.selected) return;
    this.selectMeal(this.selected, false);
  }

  saveMeal(): void {
    if (!this.selected || !this.isEditing) return;
    this.saving = true;
    const raw = this.mealForm.getRawValue();
    const payload: Partial<Meal> = {
      name: raw.name ?? '',
      likability: raw.likability ?? 80,
      active_prep_minutes: raw.active_prep_minutes ?? 20,
      cook_minutes: raw.cook_minutes ?? 20,
      make_ahead_score: raw.make_ahead_score ?? 50,
      leftover_quality: raw.leftover_quality ?? 70,
      leftover_style: raw.leftover_style ?? 'mixed',
      source_url: this.blankToNull(raw.source_url),
      source_name: this.blankToNull(raw.source_name),
      tags: this.textToTags(raw.tags_text ?? ''),
      shared_ingredients: this.textToIngredients(raw.shared_ingredients_text ?? ''),
      prep_ahead: this.textToLines(raw.prep_ahead_text ?? ''),
      instructions: this.textToLines(raw.instructions_text ?? ''),
      notes: raw.notes ?? '',
    };
    this.api.patchMeal(this.selected.id, payload).subscribe({
      next: (meal) => {
        this.saving = false;
        this.load(meal.id, false);
      },
      error: () => this.fail('Unable to save meal changes.'),
    });
  }

  archiveMeal(): void {
    if (!this.selected || !this.isEditing) return;
    const action = this.selected.status === 'active' ? this.api.archiveMeal(this.selected.id) : this.api.restoreMeal(this.selected.id);
    action.subscribe({
      next: (meal) => this.load(meal.id),
      error: () => this.fail('Unable to update meal status.'),
    });
  }

  addOption(dimension: VariationDimension): void {
    if (!this.isEditing) return;
    const name = this.newOptionNames[dimension.id]?.trim();
    if (!name) return;
    this.api.createOption(dimension.id, {
      name,
      likability: 75,
      value: this.valueForDimension(dimension.key, name),
    }).subscribe({
      next: () => {
        this.newOptionNames[dimension.id] = '';
        this.load(this.selected?.id, true);
      },
      error: () => this.fail('Unable to add option.'),
    });
  }

  updateOption(option: VariationOption, payload: Partial<VariationOption>): void {
    if (!this.isEditing) return;
    this.api.patchOption(option.id, payload).subscribe({
      next: () => this.load(this.selected?.id, true),
      error: () => this.fail('Unable to update option.'),
    });
  }

  updateOptionLines(
    option: VariationOption,
    field: 'ingredient_additions' | 'ingredient_omissions' | 'prep_ahead',
    value: string,
  ): void {
    if (field === 'ingredient_additions') {
      this.updateOption(option, { ingredient_additions: this.textToIngredients(value) });
      return;
    }
    this.updateOption(option, { [field]: this.textToLines(value) });
  }

  toggleOption(option: VariationOption): void {
    if (!this.isEditing) return;
    const action = option.status === 'active' ? this.api.archiveOption(option.id) : this.api.restoreOption(option.id);
    action.subscribe({
      next: () => this.load(this.selected?.id, true),
      error: () => this.fail('Unable to update option status.'),
    });
  }

  updateDimension(dimension: VariationDimension, payload: Partial<VariationDimension>): void {
    if (!this.isEditing) return;
    this.api.patchDimension(dimension.id, payload).subscribe({
      next: () => this.load(this.selected?.id, true),
      error: () => this.fail('Unable to update dimension.'),
    });
  }

  selectTag(tag: string): void {
    this.selectedTag = this.selectedTag === tag ? '' : tag;
  }

  clearTagFilter(): void {
    this.selectedTag = '';
  }

  sourceLabel(meal: Meal): string {
    return meal.source_name || meal.source_url || 'Source';
  }

  sourceUrlValue(): string {
    return String(this.mealForm.get('source_url')?.value ?? '').trim();
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

  private valueForDimension(key: string, name: string): Record<string, string> | string[] {
    const normalized = key.replace('variation_', '');
    if (normalized === 'vegetables') {
      return name.split(',').map((item) => item.trim()).filter(Boolean);
    }
    return { [normalized]: name };
  }

  linesToText(values: string[] = []): string {
    return values.join('\n');
  }

  tagsToText(values: string[] = []): string {
    return values.join(', ');
  }

  ingredientsToText(values: IngredientValue[] = []): string {
    return values.map((ingredient) => this.ingredientToLine(ingredient)).join('\n');
  }

  private textToLines(value: string): string[] {
    return value
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean);
  }

  private textToTags(value: string): string[] {
    return value
      .split(/[,\n]/)
      .map((tag) => tag.trim())
      .filter(Boolean)
      .filter((tag, index, tags) => tags.indexOf(tag) === index);
  }

  private blankToNull(value: string | null | undefined): string | null {
    const text = String(value ?? '').trim();
    return text || null;
  }

  private textToIngredients(value: string): IngredientItem[] {
    return this.textToLines(value).map((line) => this.lineToIngredient(line));
  }

  private lineToIngredient(line: string): IngredientItem {
    const [main, note] = line.split('|', 2).map((part) => part.trim());
    const words = main.split(/\s+/).filter(Boolean);
    if (!words.length) return { label: '' };
    const units = new Set([
      'g', 'gram', 'grams', 'oz', 'ounce', 'ounces', 'lb', 'lbs', 'pound', 'pounds',
      'ml', 'milliliter', 'milliliters', 'l', 'liter', 'liters', 'tsp', 'teaspoon', 'teaspoons',
      'tbsp', 'tablespoon', 'tablespoons', 'cup', 'cups', 'each', 'ea', 'count', 'counts',
    ]);
    const numericToken = /^(\d+(?:\.\d+)?|\d+\/\d+)$/;
    let amount = '';
    let unit = '';
    let labelStart = 0;
    if (words[0].toLowerCase() === 'to' && words[1]?.toLowerCase() === 'taste') {
      amount = 'to taste';
      labelStart = 2;
    } else if (numericToken.test(words[0])) {
      amount = words[0];
      labelStart = 1;
      if (words[1] && numericToken.test(words[1])) {
        amount = `${amount} ${words[1]}`;
        labelStart = 2;
      }
      if (words[labelStart] && units.has(words[labelStart].toLowerCase())) {
        unit = words[labelStart];
        labelStart += 1;
      }
    }
    const label = words.slice(labelStart).join(' ') || main;
    return {
      label,
      ...(amount ? { amount } : {}),
      ...(unit ? { unit } : {}),
      ...(note ? { note } : {}),
    };
  }

  private ingredientToLine(ingredient: IngredientValue): string {
    if (typeof ingredient === 'string') return ingredient;
    const amount = [ingredient.amount, ingredient.unit].filter(Boolean).join(' ');
    const main = [amount, ingredient.label].filter(Boolean).join(' ');
    return ingredient.note ? `${main} | ${ingredient.note}` : main;
  }

  private ingredientLabel(ingredient: IngredientValue): string {
    return typeof ingredient === 'string' ? ingredient : ingredient.label;
  }

  private syncFormMode(): void {
    if (this.isEditing) {
      this.mealForm.enable({ emitEvent: false });
      return;
    }
    this.mealForm.disable({ emitEvent: false });
  }

  private fail(message: string): void {
    this.error = message;
    this.saving = false;
    this.cdr.detectChanges();
  }
}
