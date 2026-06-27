# History Screen

## Purpose

The History screen shows what the household actually ate and explains why future suggestions change.

## Primary Content

- Recent meal events.
- Meal frequency table.
- Variation option frequency table grouped by meal and dimension.
- Last eaten date per meal.
- Last used date per variation option.
- Likability.
- Expected versus actual frequency.
- Feedback if recorded.
- Skipped planned meals.

## Primary Actions

- Add manual meal event.
- Edit an event.
- Delete an event created by mistake.
- Filter by meal, date range, tag, protein, or feedback.
- Open a meal in the catalog.

## Insight Requirements

- Show meals that are underused relative to likability.
- Show meals that are overused relative to likability.
- Show variation options that are underused or overused relative to option likability.
- Show meals not eaten recently.
- Show variation options not used recently within otherwise popular meals.
- Show high-likability meals that are good candidates for upcoming plans.
- History should use compact table/list rows on desktop and tablet so recent events and frequency insight can be scanned together.
- Filters and manual event inputs should use short and medium field widths instead of full-width controls for dates, feedback, counts, and meal selectors where practical.
- The Add Event section should include clear spacing between its header and the Meal dropdown below it.
- On phone-sized screens, history filters and event rows should stack without truncating important meal/date/status text.

## Acceptance Criteria

- Marking a meal eaten from Weekly Plan creates a visible history event.
- Skipped meals do not count as eaten.
- Manual history edits affect future suggestions.
- The user can answer "when did we last eat this?" without leaving the screen.
- The user can answer "when did we last use this sauce/protein/pasta/vegetable option?" without leaving the screen.
- The desktop and tablet history layout minimizes vertical scrolling for common review tasks while preserving readable event details.
