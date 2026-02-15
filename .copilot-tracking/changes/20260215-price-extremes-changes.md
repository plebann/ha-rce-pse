<!-- markdownlint-disable-file -->

# Changes: Morning/Evening Best Price Windows (Today)

## Checklist

### Phase 1: Calculator helper for top windows

- [x] Task 1.1: Add top-window selection helper
- [x] Task 1.2: Define hour bounds and duration constants for sensors

### Phase 2: New today sensors for best/second-best prices

- [x] Task 2.1: Add morning best/2nd-best price sensors
- [x] Task 2.2: Add morning best/2nd-best start timestamp sensors
- [x] Task 2.3: Add evening best/2nd-best price sensors
- [x] Task 2.4: Add evening best/2nd-best start timestamp sensors

### Phase 3: Registration, translations, and tests

- [x] Task 3.1: Register sensors in setup and exports
- [x] Task 3.2: Add translation keys for new entities
- [x] Task 3.3: Update or add tests

## Notes

- Initialized changes tracking file.
- Added `find_top_windows()` helper to rank windows with full-hour starts and distinct start hours.
- Added constants for morning/evening hour bounds and 1-hour duration.
- Added today morning/evening best and second-best price sensors plus start timestamps.
- Registered new sensors and added translations in English and Polish.
- Added tests for top-window selection and new best-window sensors.