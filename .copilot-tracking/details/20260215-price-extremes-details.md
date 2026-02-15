<!-- markdownlint-disable-file -->

# Task Details: Morning/Evening Best Price Windows (Today)

## Research Reference

**Source Research**: #file:../research/20260215-price-extremes-research.md

## Phase 1: Calculator helper for top windows

### Task 1.1: Add top-window selection helper

Create a `find_top_windows()` helper in `PriceCalculator` that enumerates all continuous windows inside a time range, ranks them by average price, and returns the top-N windows with distinct start hours.

- **Files**:
  - custom_components/rce_pse/price_calculator.py - add helper based on `find_optimal_window()` rules, enforce full-hour starts.
- **Success**:
  - Helper accepts window bounds, duration in hours, and returns up to two windows sorted by highest average price.
  - Only windows that start at minute 00 are eligible.
- **Research References**:
  - #file:../research/20260215-price-extremes-research.md (Lines 114-151) - top-N window selection and full-hour constraint.
  - #file:../research/20260215-price-extremes-research.md (Lines 140-151) - algorithm outline derived from `find_optimal_window()`.
- **Dependencies**:
  - Existing `find_optimal_window()` continuity logic and `rce_pln` data shape.

### Task 1.2: Define hour bounds and duration constants for sensors

Specify morning (07-09) and evening (17-21) bounds with a 1-hour window duration in the new sensors.

- **Files**:
  - custom_components/rce_pse/sensors - new or existing module for today-only best window sensors.
- **Success**:
  - Morning window uses hours 7-9; evening uses 17-21.
  - Window duration is 1 hour; only full-hour starts are valid.
- **Research References**:
  - #file:../research/20260215-price-extremes-research.md (Lines 114-121) - time windows and full-hour requirement.
- **Dependencies**:
  - Task 1.1 completion.

## Phase 2: New today sensors for best/second-best prices

### Task 2.1: Add morning best/2nd-best price sensors

Create today-only sensors that expose the highest and second-highest average prices for the morning window (07-09), using distinct start hours.

- **Files**:
  - custom_components/rce_pse/sensors - add two price sensors.
- **Success**:
  - `morning_best_price` returns the highest average window price.
  - `morning_2nd_best_price` returns the next window with a different start hour (price may match the best).
- **Research References**:
  - #file:../research/20260215-price-extremes-research.md (Lines 154-167) - distinct start hour rule and sensor outputs.
- **Dependencies**:
  - Task 1.1 completion.

### Task 2.2: Add morning best/2nd-best start timestamp sensors

Create today-only timestamp sensors that expose the start time of the best and second-best morning windows.

- **Files**:
  - custom_components/rce_pse/sensors - add two timestamp sensors.
- **Success**:
  - Timestamps align with window start times (minute 00).
  - Timestamp construction matches existing hour-start timestamp patterns.
- **Research References**:
  - #file:../research/20260215-price-extremes-research.md (Lines 163-167) - output consumption and timestamp rules.
- **Dependencies**:
  - Task 2.1 completion.

### Task 2.3: Add evening best/2nd-best price sensors

Create today-only sensors that expose the highest and second-highest average prices for the evening window (17-21).

- **Files**:
  - custom_components/rce_pse/sensors - add two price sensors.
- **Success**:
  - `evening_best_price` returns the highest average window price.
  - `evening_2nd_best_price` returns the next window with a different start hour.
- **Research References**:
  - #file:../research/20260215-price-extremes-research.md (Lines 114-121) - evening time window and full-hour requirement.
- **Dependencies**:
  - Task 1.1 completion.

### Task 2.4: Add evening best/2nd-best start timestamp sensors

Create today-only timestamp sensors that expose the start time of the best and second-best evening windows.

- **Files**:
  - custom_components/rce_pse/sensors - add two timestamp sensors.
- **Success**:
  - Timestamps align with window start times (minute 00).
  - Timestamp construction matches existing hour-start timestamp patterns.
- **Research References**:
  - #file:../research/20260215-price-extremes-research.md (Lines 163-167) - output consumption and timestamp rules.
- **Dependencies**:
  - Task 2.3 completion.

## Phase 3: Registration, translations, and tests

### Task 3.1: Register sensors in setup and exports

Register the new sensors in the sensor setup list and public exports.

- **Files**:
  - custom_components/rce_pse/sensors/__init__.py - add new class exports.
  - custom_components/rce_pse/sensor.py - add new sensor instances.
- **Success**:
  - All new sensors are instantiated in setup.
  - Exports include the new class names.
- **Research References**:
  - #file:../research/20260215-price-extremes-research.md (Lines 47-57) - current sensor catalog for placement.
- **Dependencies**:
  - Phase 2 completion.

### Task 3.2: Add translation keys for new entities

Add entity names for the new sensors in translation files.

- **Files**:
  - custom_components/rce_pse/translations/en.json - add names for new sensors.
  - custom_components/rce_pse/translations/pl.json - add matching names.
- **Success**:
  - All new entity keys have names in English and Polish.
- **Research References**:
  - #file:../research/20260215-price-extremes-research.md (Lines 118-121) - translation keys required in implementation guidance.
- **Dependencies**:
  - Phase 2 completion.

### Task 3.3: Update or add tests

Add tests validating the top-window selection logic and sensor outputs for morning/evening cases.

- **Files**:
  - tests - add or update test modules for window selection and new sensors.
- **Success**:
  - Tests cover full-hour window filtering, distinct start hour selection, and top-two window ordering.
- **Research References**:
  - #file:../research/20260215-price-extremes-research.md (Lines 114-167) - selection rules and outputs.
- **Dependencies**:
  - Phase 1 completion.

## Dependencies

- Python 3.11+ runtime for Home Assistant integration tests.

## Success Criteria

- New morning/evening best and 2nd-best sensors are available for today with correct prices and timestamps.
- Window selection respects 07-09 and 17-21 bounds, full-hour starts, and distinct start hours.
- Translations exist for all new entities.