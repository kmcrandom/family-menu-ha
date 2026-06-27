import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { ApiService } from '../core/api.service';
import { DietaryProfile, HouseholdConfig, HouseholdMember, ImportDataResponse, Preferences } from '../core/models';
import { MATERIAL_IMPORTS } from '../shared/material';

interface ImportConfirmData {
  fileName: string;
}

@Component({
  selector: 'app-import-confirm-dialog',
  imports: [MATERIAL_IMPORTS],
  template: `
    <h2 mat-dialog-title>Restore Family Menu Data?</h2>
    <mat-dialog-content>
      <p>
        Importing {{ data.fileName }} will replace the current meal catalog, household config, weekly plans,
        vacation blocks, history, and checklist state.
      </p>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button type="button" (click)="dialogRef.close(false)">Cancel</button>
      <button mat-flat-button color="warn" type="button" (click)="dialogRef.close(true)">Restore</button>
    </mat-dialog-actions>
  `,
})
export class ImportConfirmDialogComponent {
  readonly data = inject<ImportConfirmData>(MAT_DIALOG_DATA);
  readonly dialogRef = inject(MatDialogRef<ImportConfirmDialogComponent>);
}

@Component({
  selector: 'app-settings',
  imports: [CommonModule, FormsModule, ReactiveFormsModule, MATERIAL_IMPORTS],
  templateUrl: './settings.component.html',
})
export class SettingsComponent {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly dialog = inject(MatDialog);

  saved = false;
  error = '';
  importMessage = '';
  household?: HouseholdConfig;
  newMemberName = '';
  newProfileName = '';
  newProfileType: DietaryProfile['type'] = 'custom';
  newProfileExcludedTags = '';
  selectedImportFile?: File;
  selectedImportData?: Record<string, unknown>;

  readonly form = this.fb.group({
    household_name: ['Family Menu'],
    mixed_diet_mode: ['separate_variations'],
    week_start_day: ['Sunday'],
    shopping_day: ['Sunday'],
    default_week_size: [5],
    default_dinner_servings: [4],
    default_leftover_lunch_servings: [2],
    max_same_meal_per_week: [1],
    soft_repeat_gap_days: [14],
    avoid_consecutive_leftover_styles: [true],
    variation_recency_weight: [0.45],
    variation_frequency_weight: [0.35],
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.api.getHousehold().subscribe({
      next: (household) => this.applyHousehold(household),
      error: () => this.fail('Unable to load family config.'),
    });
  }

  save(): void {
    this.saved = false;
    this.api.patchPreferences(this.form.getRawValue() as Partial<Preferences>).subscribe({
      next: (preferences) => {
        this.form.patchValue(preferences);
        this.api.getHousehold().subscribe({
          next: (household) => {
            this.applyHousehold(household);
            this.saved = true;
            this.cdr.detectChanges();
          },
          error: () => this.fail('Settings saved, but unable to reload family config.'),
        });
      },
      error: () => this.fail('Unable to save settings.'),
    });
  }

  addMember(): void {
    const displayName = this.newMemberName.trim();
    if (!displayName) return;
    const firstProfile = this.household?.dietary_profiles[0]?.id;
    this.api
      .createHouseholdMember({
        display_name: displayName,
        dinner_servings: 1,
        leftover_lunch_servings: 0,
        dietary_profile_ids: firstProfile ? [firstProfile] : [],
      })
      .subscribe({
        next: () => {
          this.newMemberName = '';
          this.load();
        },
        error: () => this.fail('Unable to add household member.'),
      });
  }

  saveMember(member: HouseholdMember): void {
    this.api.patchHouseholdMember(member.id, member).subscribe({
      next: () => this.load(),
      error: () => this.fail('Unable to save household member.'),
    });
  }

  setMemberProfile(member: HouseholdMember, profileId: string): void {
    member.dietary_profile_ids = profileId ? [profileId] : [];
    this.saveMember(member);
  }

  addProfile(): void {
    const name = this.newProfileName.trim();
    if (!name) return;
    this.api
      .createDietaryProfile({
        name,
        type: this.newProfileType,
        excluded_tags: this.tagsFromText(this.newProfileExcludedTags),
      })
      .subscribe({
        next: () => {
          this.newProfileName = '';
          this.newProfileType = 'custom';
          this.newProfileExcludedTags = '';
          this.load();
        },
        error: () => this.fail('Unable to add dietary profile.'),
      });
  }

  saveProfile(profile: DietaryProfile, excludedTagsText: string): void {
    this.api
      .patchDietaryProfile(profile.id, {
        name: profile.name,
        type: profile.type,
        excluded_tags: this.tagsFromText(excludedTagsText),
        included_tags: profile.included_tags,
        notes: profile.notes,
      })
      .subscribe({
        next: () => this.load(),
        error: () => this.fail('Unable to save dietary profile.'),
      });
  }

  tagsText(tags: string[] = []): string {
    return tags.join(', ');
  }

  exportUrl(): string {
    return '/api/v1/export';
  }

  selectImportFile(event: Event): void {
    this.error = '';
    this.importMessage = '';
    this.selectedImportFile = undefined;
    this.selectedImportData = undefined;
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(String(reader.result || ''));
        if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
          throw new Error('Import file must be a JSON object.');
        }
        this.selectedImportFile = file;
        this.selectedImportData = parsed as Record<string, unknown>;
        this.cdr.detectChanges();
      } catch {
        this.fail('Unable to read import JSON.');
        input.value = '';
      }
    };
    reader.onerror = () => {
      this.fail('Unable to read import file.');
      input.value = '';
    };
    reader.readAsText(file);
  }

  importSelectedFile(): void {
    if (!this.selectedImportFile || !this.selectedImportData) {
      this.fail('Choose an export JSON file first.');
      return;
    }
    const dialogRef = this.dialog.open(ImportConfirmDialogComponent, {
      data: { fileName: this.selectedImportFile.name },
      width: '440px',
    });
    dialogRef.afterClosed().subscribe((confirmed) => {
      if (!confirmed || !this.selectedImportData) return;
      this.api.importData(this.selectedImportData, true).subscribe({
        next: (response) => this.finishImport(response),
        error: (err) => this.fail(err?.error?.detail || 'Unable to import data.'),
      });
    });
  }

  private applyHousehold(household: HouseholdConfig): void {
    this.household = household;
    this.form.patchValue(household.preferences);
    this.error = '';
    this.cdr.detectChanges();
  }

  private finishImport(response: ImportDataResponse): void {
    this.selectedImportFile = undefined;
    this.selectedImportData = undefined;
    this.applyHousehold(response.household);
    this.importMessage = `Imported ${response.imported['meals'] || 0} meals, ${response.imported['plans'] || 0} plans, and ${response.imported['events'] || 0} history events.`;
    this.cdr.detectChanges();
  }

  private tagsFromText(value: string): string[] {
    return value
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean);
  }

  private fail(message: string): void {
    this.error = message;
    this.importMessage = '';
    this.cdr.detectChanges();
  }
}
