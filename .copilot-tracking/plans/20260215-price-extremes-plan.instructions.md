---
applyTo: ".copilot-tracking/changes/20260215-price-extremes-changes.md"
---

<!-- markdownlint-disable-file -->

# Task Checklist: Morning/Evening Best Price Windows (Today)

## Overview

Plan the changes needed to add today-only morning/evening best and second-best price sensors (with start timestamps) using full-hour windows.

## Objectives

- Add a calculator helper to select the top two windows by highest average price with distinct start hours and full-hour starts.
- Introduce today-only morning/evening best and second-best price sensors with start timestamps and translations.

## Research Summary

### Project Files

- custom_components/rce_pse/price_calculator.py - existing window selection logic and data shape.
- custom_components/rce_pse/sensors/custom_windows.py - current window sensor patterns and timestamp handling.
- custom_components/rce_pse/sensor.py - sensor registration list.
- custom_components/rce_pse/translations/en.json - entity name mappings.

### External References

- #file:../research/20260215-price-extremes-research.md - requirements, algorithm outline, and sensor list.

### Standards References

- No additional standards or instruction files found in this repository.

## Implementation Checklist

### [ ] Phase 1: Calculator helper for top windows

- [ ] Task 1.1: Add top-window selection helper

  - Details: .copilot-tracking/details/20260215-price-extremes-details.md (Lines 11-24)

- [ ] Task 1.2: Define hour bounds and duration constants for sensors
  - Details: .copilot-tracking/details/20260215-price-extremes-details.md (Lines 26-38)

### [ ] Phase 2: New today sensors for best/second-best prices

- [ ] Task 2.1: Add morning best/2nd-best price sensors
  - Details: .copilot-tracking/details/20260215-price-extremes-details.md (Lines 42-54)

- [ ] Task 2.2: Add morning best/2nd-best start timestamp sensors
  - Details: .copilot-tracking/details/20260215-price-extremes-details.md (Lines 56-68)

- [ ] Task 2.3: Add evening best/2nd-best price sensors
  - Details: .copilot-tracking/details/20260215-price-extremes-details.md (Lines 70-82)

- [ ] Task 2.4: Add evening best/2nd-best start timestamp sensors
  - Details: .copilot-tracking/details/20260215-price-extremes-details.md (Lines 84-96)

### [ ] Phase 3: Registration, translations, and tests

- [ ] Task 3.1: Register sensors in setup and exports
  - Details: .copilot-tracking/details/20260215-price-extremes-details.md (Lines 100-113)

- [ ] Task 3.2: Add translation keys for new entities
  - Details: .copilot-tracking/details/20260215-price-extremes-details.md (Lines 115-127)

- [ ] Task 3.3: Update or add tests
  - Details: .copilot-tracking/details/20260215-price-extremes-details.md (Lines 129-140)

## Dependencies

- Python 3.11+ runtime for Home Assistant integration tests.

## Success Criteria

- Morning and evening best/second-best sensors for today report correct prices and timestamps.
- Window selection enforces 07-09 and 17-21 bounds, full-hour starts, and distinct start hours.