import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MATERIAL_IMPORTS } from './shared/material';

@Component({
  selector: 'app-root',
  imports: [RouterLink, RouterLinkActive, RouterOutlet, MATERIAL_IMPORTS],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  readonly navItems = [
    { path: '/weekly-plan', label: 'Weekly Plan', icon: 'event_note' },
    { path: '/meal-catalog', label: 'Meal Catalog', icon: 'restaurant_menu' },
    { path: '/grocery-prep', label: 'Grocery + Prep', icon: 'shopping_cart' },
    { path: '/history', label: 'History', icon: 'history' },
    { path: '/settings', label: 'Family Config', icon: 'settings' },
  ];
}
