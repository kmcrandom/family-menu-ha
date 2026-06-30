import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { IngredientItem, IngredientValue, Meal, VariationDimension, VariationOption } from '../core/models';
import { MATERIAL_IMPORTS } from '../shared/material';

interface VariationTypeChoice {
  key: string;
  name: string;
  color: string;
  builtIn?: boolean;
}

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
  isCreatingMeal = false;
  isMealMenuOpen = false;
  previousSelectedMealId = '';
  newOptionNames: Record<string, string> = {};
  newDimensionKey = '';
  newDimensionName = '';
  newDimensionCustomKey = '';
  newDimensionRequired = false;
  newDimensionColor = '';
  showAddDimensionPanel = false;

  readonly customDimensionKey = '__custom__';
  readonly materialColors = [
    '#f44336', '#e91e63', '#9c27b0', '#673ab7',
    '#3f51b5', '#2196f3', '#03a9f4', '#009688',
    '#4caf50', '#8bc34a', '#ffc107', '#ff9800',
    '#ff5722', '#795548', '#607d8b',
  ];

  readonly builtInVariationTypes: VariationTypeChoice[] = [
    { key: 'variation_primary_protein', name: 'Primary protein', color: '#f44336', builtIn: true },
    { key: 'variation_diet_protein', name: 'Pescatarian protein', color: '#009688', builtIn: true },
    { key: 'variation_vegetables', name: 'Vegetables', color: '#4caf50', builtIn: true },
    { key: 'variation_sauce', name: 'Sauce', color: '#ffc107', builtIn: true },
    { key: 'variation_starch_or_base', name: 'Starch/base', color: '#3f51b5', builtIn: true },
    { key: 'variation_toppings', name: 'Toppings', color: '#e91e63', builtIn: true },
    { key: 'variation_prep_method', name: 'Prep method', color: '#607d8b', builtIn: true },
  ];

  readonly mealForm = this.fb.group({
    name: [''],
    likability: [null as number | null],
    active_prep_minutes: [null as number | null],
    cook_minutes: [null as number | null],
    make_ahead_score: [null as number | null],
    leftover_quality: [null as number | null],
    leftover_style: [''],
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

  get activeDimensions(): VariationDimension[] {
    return this.selected?.variation_dimensions.filter((dimension) => dimension.status === 'active') ?? [];
  }

  get selectedTitle(): string {
    if (!this.isCreatingMeal) return this.selected?.name ?? '';
    const name = String(this.mealForm.get('name')?.value ?? '').trim();
    return name || 'New meal';
  }

  get reusableVariationTypes(): VariationTypeChoice[] {
    const activeKeys = new Set(this.activeDimensions.map((dimension) => dimension.key));
    const byKey = new Map<string, VariationTypeChoice>();
    for (const type of this.builtInVariationTypes) {
      byKey.set(type.key, type);
    }
    for (const meal of this.meals) {
      for (const dimension of meal.variation_dimensions) {
        if (dimension.status === 'archived') continue;
        if (!byKey.has(dimension.key)) {
          byKey.set(dimension.key, {
            key: dimension.key,
            name: dimension.name,
            color: dimension.color || this.fallbackColorForKey(dimension.key),
          });
        }
      }
    }
    return [...byKey.values()]
      .filter((type) => !activeKeys.has(type.key))
      .sort((a, b) => Number(Boolean(b.builtIn)) - Number(Boolean(a.builtIn)) || a.name.localeCompare(b.name));
  }

  get usedDimensionColors(): Set<string> {
    return new Set(this.activeDimensions.map((dimension) => this.normalizeColor(dimension.color)).filter(Boolean));
  }

  get availableMaterialColors(): string[] {
    const used = this.usedDimensionColors;
    return this.materialColors.filter((color) => !used.has(this.normalizeColor(color)));
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
    if (this.isCreatingMeal && this.isEditing) {
      if (!window.confirm('Discard this new meal draft?')) return;
      this.isCreatingMeal = false;
      this.previousSelectedMealId = '';
    }
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
    this.resetNewDimension(true);
    this.syncFormMode();
    this.closeMealMenu();
  }

  startCreatingMeal(): void {
    this.previousSelectedMealId = this.isCreatingMeal ? this.previousSelectedMealId : this.selected?.id ?? '';
    this.isCreatingMeal = true;
    this.error = '';
    this.selected = this.newMealDraft();
    this.isEditing = true;
    this.mealForm.reset(this.defaultMealFormValue());
    this.resetNewDimension(true);
    this.syncFormMode();
    this.closeMealMenu();
  }

  startEditing(): void {
    if (!this.selected) return;
    this.isEditing = true;
    this.syncFormMode();
  }

  cancelEditing(): void {
    if (!this.selected) return;
    if (this.isCreatingMeal) {
      const previous = this.meals.find((meal) => meal.id === this.previousSelectedMealId);
      this.isCreatingMeal = false;
      this.previousSelectedMealId = '';
      this.error = '';
      if (previous) {
        this.selectMeal(previous, false);
        return;
      }
      this.selected = undefined;
      this.isEditing = false;
      this.mealForm.reset(this.defaultMealFormValue());
      this.resetNewDimension(true);
      this.syncFormMode();
      return;
    }
    this.selectMeal(this.selected, false);
  }

  saveMeal(): void {
    if (!this.selected || !this.isEditing) return;
    const payload = this.mealPayloadFromForm();
    if (this.isCreatingMeal && !String(payload.name ?? '').trim()) {
      this.error = 'Meal name is required.';
      return;
    }
    this.saving = true;
    const request = this.isCreatingMeal
      ? this.api.createMeal(payload)
      : this.api.patchMeal(this.selected.id, payload);
    request.subscribe({
      next: (meal) => {
        this.saving = false;
        this.isCreatingMeal = false;
        this.previousSelectedMealId = '';
        this.error = '';
        this.load(meal.id, false);
      },
      error: () => this.fail(this.isCreatingMeal ? 'Unable to create meal.' : 'Unable to save meal changes.'),
    });
  }

  archiveMeal(): void {
    if (!this.selected || this.isEditing) return;
    if (this.selected.status === 'active' && !window.confirm(`Archive ${this.selected.name}?`)) return;
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

  openAddDimensionPanel(): void {
    if (!this.isEditing) return;
    this.showAddDimensionPanel = true;
  }

  closeAddDimensionPanel(): void {
    this.resetNewDimension(true);
  }

  selectNewDimensionType(key: string): void {
    this.newDimensionKey = key;
    if (key === this.customDimensionKey) {
      this.newDimensionName = '';
      this.newDimensionCustomKey = '';
      this.newDimensionColor = this.availableMaterialColors[0] ?? '#9e9e9e';
      return;
    }
    const choice = this.reusableVariationTypes.find((type) => type.key === key);
    if (!choice) return;
    this.newDimensionName = choice.name;
    this.newDimensionCustomKey = choice.key;
    this.newDimensionColor = this.availableMaterialColors.includes(choice.color)
      ? choice.color
      : this.availableMaterialColors[0] ?? choice.color;
  }

  addDimension(): void {
    if (!this.selected || !this.isEditing || !this.newDimensionKey) return;
    const name = this.newDimensionName.trim();
    if (!name) return;
    const key = this.newDimensionKey === this.customDimensionKey
      ? this.normalizeDimensionKey(this.newDimensionCustomKey || name)
      : this.newDimensionKey;
    this.api.createDimension(this.selected.id, {
      key,
      name,
      selection_mode: 'single',
      required: this.newDimensionRequired,
      display_order: this.activeDimensions.length,
      color: this.newDimensionColor || null,
    }).subscribe({
      next: () => {
        this.resetNewDimension(true);
        this.load(this.selected?.id, true);
      },
      error: () => this.fail('Unable to add variation.'),
    });
  }

  archiveDimension(dimension: VariationDimension): void {
    if (!this.isEditing) return;
    const suffix = dimension.options.length ? ` This also hides ${dimension.options.length} options from future suggestions.` : '';
    if (!window.confirm(`Remove ${dimension.name} from this meal?${suffix}`)) return;
    this.api.archiveDimension(dimension.id).subscribe({
      next: () => this.load(this.selected?.id, true),
      error: () => this.fail('Unable to remove variation.'),
    });
  }

  selectTag(tag: string): void {
    this.selectedTag = this.selectedTag === tag ? '' : tag;
  }

  clearTagFilter(): void {
    this.selectedTag = '';
  }

  openMealMenu(): void {
    this.isMealMenuOpen = true;
  }

  closeMealMenu(): void {
    this.isMealMenuOpen = false;
  }

  sourceLabel(meal: Meal): string {
    return meal.source_name || meal.source_url || 'Source';
  }

  sourceUrlValue(): string {
    return String(this.mealForm.get('source_url')?.value ?? '').trim();
  }

  variationToneClass(dimension: VariationDimension): string {
    if (dimension.color) return 'variation-tone-custom';
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

  variationToneStyle(dimension: VariationDimension): Record<string, string> {
    if (!dimension.color) return {};
    const color = dimension.color;
    return {
      '--tone-border': color,
      '--tone-bg': `color-mix(in srgb, ${color} 18%, var(--surface-2))`,
      '--tone-text': `color-mix(in srgb, ${color} 55%, var(--text))`,
    };
  }

  fallbackColorForKey(key: string): string {
    const normalized = key.toLowerCase();
    if (normalized.includes('primary_protein')) return '#f44336';
    if (normalized.includes('diet_protein') || normalized.includes('pescatarian')) return '#009688';
    if (normalized.includes('vegetable')) return '#4caf50';
    if (normalized.includes('sauce')) return '#ffc107';
    if (normalized.includes('starch') || normalized.includes('base') || normalized.includes('pasta')) return '#3f51b5';
    if (normalized.includes('topping')) return '#e91e63';
    if (normalized.includes('prep')) return '#607d8b';
    return '#9e9e9e';
  }

  availableMaterialColorsForDimension(dimension: VariationDimension): string[] {
    const current = this.normalizeColor(dimension.color);
    const used = this.usedDimensionColors;
    return this.materialColors.filter((color) => {
      const normalized = this.normalizeColor(color);
      return normalized === current || !used.has(normalized);
    });
  }

  colorSelected(dimension: VariationDimension, color: string): boolean {
    return this.normalizeColor(dimension.color) === this.normalizeColor(color);
  }

  private valueForDimension(key: string, name: string): Record<string, string> | string[] {
    const normalized = key.replace('variation_', '');
    if (normalized === 'vegetables') {
      return name.split(',').map((item) => item.trim()).filter(Boolean);
    }
    return { [normalized]: name };
  }

  private resetNewDimension(closePanel = false): void {
    this.newDimensionKey = '';
    this.newDimensionName = '';
    this.newDimensionCustomKey = '';
    this.newDimensionRequired = false;
    this.newDimensionColor = this.availableMaterialColors[0] ?? '#9e9e9e';
    if (closePanel) this.showAddDimensionPanel = false;
  }

  private normalizeDimensionKey(value: string): string {
    const slug = value
      .trim()
      .toLowerCase()
      .replace(/^variation[_-]?/, '')
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
    return `variation_${slug || 'custom'}`;
  }

  private normalizeColor(value?: string | null): string {
    return String(value ?? '').trim().toLowerCase();
  }

  private mealPayloadFromForm(): Partial<Meal> {
    const raw = this.mealForm.getRawValue();
    const numericPayload = this.isCreatingMeal
      ? {
          ...this.createNumberPayload('likability', raw.likability),
          ...this.createNumberPayload('active_prep_minutes', raw.active_prep_minutes),
          ...this.createNumberPayload('cook_minutes', raw.cook_minutes),
          ...this.createNumberPayload('make_ahead_score', raw.make_ahead_score),
          ...this.createNumberPayload('leftover_quality', raw.leftover_quality),
        }
      : {
          likability: this.numberOrDefault(raw.likability, 80),
          active_prep_minutes: this.numberOrDefault(raw.active_prep_minutes, 20),
          cook_minutes: this.numberOrDefault(raw.cook_minutes, 20),
          make_ahead_score: this.numberOrDefault(raw.make_ahead_score, 50),
          leftover_quality: this.numberOrDefault(raw.leftover_quality, 70),
        };
    return {
      name: String(raw.name ?? '').trim(),
      ...numericPayload,
      ...(this.isCreatingMeal && !String(raw.leftover_style ?? '').trim()
        ? {}
        : { leftover_style: String(raw.leftover_style ?? '').trim() || 'mixed' }),
      source_url: this.blankToNull(raw.source_url),
      source_name: this.blankToNull(raw.source_name),
      tags: this.textToTags(raw.tags_text ?? ''),
      shared_ingredients: this.textToIngredients(raw.shared_ingredients_text ?? ''),
      prep_ahead: this.textToLines(raw.prep_ahead_text ?? ''),
      instructions: this.textToLines(raw.instructions_text ?? ''),
      notes: raw.notes ?? '',
    };
  }

  private newMealDraft(): Meal {
    return {
      id: '__new_meal__',
      name: 'New meal',
      status: 'active',
      likability: 80,
      active_prep_minutes: 20,
      cook_minutes: 20,
      make_ahead_score: 50,
      leftover_quality: 70,
      leftover_style: 'mixed',
      tags: [],
      diet_tags: [],
      shared_ingredients: [],
      primary_proteins: [],
      alternate_proteins: [],
      prep_ahead: [],
      instructions: [],
      source_url: null,
      source_name: null,
      simple_serving_variations: [],
      notes: '',
      variation_dimensions: [],
    };
  }

  private defaultMealFormValue(): Record<string, string | number | null> {
    return {
      name: '',
      likability: null,
      active_prep_minutes: null,
      cook_minutes: null,
      make_ahead_score: null,
      leftover_quality: null,
      leftover_style: '',
      source_url: '',
      source_name: '',
      tags_text: '',
      shared_ingredients_text: '',
      prep_ahead_text: '',
      instructions_text: '',
      notes: '',
    };
  }

  private createNumberPayload(key: keyof Pick<Meal, 'likability' | 'active_prep_minutes' | 'cook_minutes' | 'make_ahead_score' | 'leftover_quality'>, value: unknown): Partial<Meal> {
    const parsed = this.optionalNumber(value);
    return parsed === undefined ? {} : { [key]: parsed };
  }

  private optionalNumber(value: unknown): number | undefined {
    if (value === null || value === undefined || value === '') return undefined;
    const parsed = Number(value);
    return Number.isNaN(parsed) ? undefined : parsed;
  }

  private numberOrDefault(value: unknown, fallback: number): number {
    return this.optionalNumber(value) ?? fallback;
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
