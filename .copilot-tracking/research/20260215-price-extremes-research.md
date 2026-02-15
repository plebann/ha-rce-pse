<!-- markdownlint-disable-file -->

# Task Research Notes: Price extremes (today/tomorrow) calculation

## Research Executed

### File Analysis

- custom_components/rce_pse/price_calculator.py
  - Extreme price selection uses `rce_pln` values; returns all records equal to the extreme and sorts by `dtime`.
- custom_components/rce_pse/sensors/today_stats.py
  - Today max/min sensors compute `max()`/`min()` over `rce_pln` prices.
- custom_components/rce_pse/sensors/tomorrow_stats.py
  - Tomorrow max/min sensors compute `max()`/`min()` over `rce_pln` prices; availability depends on tomorrow data.
- custom_components/rce_pse/sensors/today_hours.py
  - Start/end/range sensors use the first and last extreme records' `period` values.
- custom_components/rce_pse/sensors/tomorrow_hours.py
  - Start/end/range sensors use the first and last extreme records' `period` values for tomorrow data.
- custom_components/rce_pse/binary_sensors/price_windows.py
  - Binary sensors use the same first/last extreme `period` as a window without continuity checks.

### Code Search Results

- max|min|maximum|minimum
  - Matches in price calculators and today/tomorrow stats/hours sensors for min/max computation and extreme record lookup.
- find_extreme_price_records
  - Used across today/tomorrow hour and window sensors for start/end/range derivation.

### External Research

- None (no external sources consulted).

### Project Conventions

- Standards referenced: none found (no copilot/ or .github/instructions in workspace).
- Instructions followed: repository contains .github/workflows only.

## Key Discoveries

### Project Structure

Price statistics are split into:
- Stats sensors for today/tomorrow min/max/avg/median values.
- Hour and range sensors for start/end and ranges derived from extreme price records.
- Binary sensors that flag whether the current time is within the extreme price window.

Defined sensors grouped by category (from sensor setup files):
- Today main/price: `RCETodayMainSensor`, `RCETodayKwhPriceSensor`, `RCENextHourPriceSensor`, `RCENext2HoursPriceSensor`, `RCENext3HoursPriceSensor`, `RCEPreviousHourPriceSensor`.
- Today stats: `RCETodayAvgPriceSensor`, `RCETodayMaxPriceSensor`, `RCETodayMinPriceSensor`, `RCETodayMedianPriceSensor`, `RCETodayCurrentVsAverageSensor`.
- Today hours/ranges: `RCETodayMaxPriceHourStartSensor`, `RCETodayMaxPriceHourEndSensor`, `RCETodayMinPriceHourStartSensor`, `RCETodayMinPriceHourEndSensor`, `RCETodayMaxPriceHourStartTimestampSensor`, `RCETodayMaxPriceHourEndTimestampSensor`, `RCETodayMinPriceHourStartTimestampSensor`, `RCETodayMinPriceHourEndTimestampSensor`, `RCETodayMinPriceRangeSensor`, `RCETodayMaxPriceRangeSensor`.
- Tomorrow main: `RCETomorrowMainSensor`.
- Tomorrow stats: `RCETomorrowAvgPriceSensor`, `RCETomorrowMaxPriceSensor`, `RCETomorrowMinPriceSensor`, `RCETomorrowMedianPriceSensor`, `RCETomorrowTodayAvgComparisonSensor`.
- Tomorrow hours/ranges: `RCETomorrowMaxPriceHourStartSensor`, `RCETomorrowMaxPriceHourEndSensor`, `RCETomorrowMinPriceHourStartSensor`, `RCETomorrowMinPriceHourEndSensor`, `RCETomorrowMaxPriceHourStartTimestampSensor`, `RCETomorrowMaxPriceHourEndTimestampSensor`, `RCETomorrowMinPriceHourStartTimestampSensor`, `RCETomorrowMinPriceHourEndTimestampSensor`, `RCETomorrowMinPriceRangeSensor`, `RCETomorrowMaxPriceRangeSensor`.
- Custom windows (today): `RCETodayCheapestWindowStartSensor`, `RCETodayCheapestWindowEndSensor`, `RCETodayCheapestWindowRangeSensor`, `RCETodayExpensiveWindowStartSensor`, `RCETodayExpensiveWindowEndSensor`, `RCETodayExpensiveWindowRangeSensor`, `RCETodayCheapestWindowStartTimestampSensor`, `RCETodayCheapestWindowEndTimestampSensor`, `RCETodayExpensiveWindowStartTimestampSensor`, `RCETodayExpensiveWindowEndTimestampSensor`.
- Custom windows (tomorrow): `RCETomorrowCheapestWindowStartSensor`, `RCETomorrowCheapestWindowEndSensor`, `RCETomorrowCheapestWindowRangeSensor`, `RCETomorrowExpensiveWindowStartSensor`, `RCETomorrowExpensiveWindowEndSensor`, `RCETomorrowExpensiveWindowRangeSensor`, `RCETomorrowCheapestWindowStartTimestampSensor`, `RCETomorrowCheapestWindowEndTimestampSensor`, `RCETomorrowExpensiveWindowStartTimestampSensor`, `RCETomorrowExpensiveWindowEndTimestampSensor`.
- Binary sensors (price windows): `RCETodayMinPriceWindowBinarySensor`, `RCETodayMaxPriceWindowBinarySensor`.
- Binary sensors (custom windows): `RCETodayCheapestWindowBinarySensor`, `RCETodayExpensiveWindowBinarySensor`.

### Implementation Patterns

- `PriceCalculator.find_extreme_price_records()` selects the extreme `rce_pln` value and returns all matching records sorted by `dtime`.
- Today/tomorrow max/min sensors simply call `max()`/`min()` on the list of `rce_pln` values from data.
- Hour start/end/range sensors use the first and last records in the sorted extreme list, extracting `period` text to get times.
- Binary sensors treat the first/last extreme period as a window; no continuity validation exists, so a range may span gaps.
- Custom windows already exist via `find_optimal_window()`, using configurable start/end hours and duration with continuity checks (15-minute cadence).
- Tomorrow availability is gated by `is_tomorrow_data_available()` which returns true only after 14:00 local time.
- `find_optimal_window()` currently returns a single best window by average price; it does not expose rankings or multiple windows.

### Complete Examples

```python
@staticmethod
def find_extreme_price_records(data: list[dict], is_max: bool = True) -> list[dict]:
    if not data:
        return []

    prices = PriceCalculator.get_prices_from_data(data)
    extreme_price = max(prices) if is_max else min(prices)

    extreme_records = [
        record for record in data
        if float(record["rce_pln"]) == extreme_price
    ]

    return sorted(extreme_records, key=lambda x: x["dtime"])
```

  ```python
  def find_optimal_window(data: list[dict], window_start_hour: int, window_end_hour: int,
              duration_hours: int, is_max: bool = False) -> list[dict]:
    # Filters data by window hours, enforces 15-min continuity, then picks best avg.
    ...
  ```

### API and Schema Documentation

- Data records are expected to have `rce_pln`, `dtime` in `%Y-%m-%d %H:%M:%S`, and `period` like `HH:MM - HH:MM`.

### Configuration Examples

```text
N/A (no configuration examples relevant to min/max calculation in this research).
```

### Technical Requirements

- Min/max values operate on `rce_pln` floats, not `rce_pln_neg_to_zero`.
- Extreme ranges derive from first/last occurrence of extreme price, not guaranteed to be contiguous.
- 15-minute cadence assumptions appear in `find_optimal_window()` continuity checks (used for custom windows, not extremes).
- The existing custom window sensors already provide a pattern for time-bounded windows (start/end/duration) and reuse the same calculator.

## Recommended Approach

Add a calculator helper that enumerates all continuous windows within a time range (same filtering and continuity rules as `find_optimal_window()`), calculates average price per window, and returns the top-N windows by highest average price with distinct start hours. Enforce "full" windows that start on the hour (e.g., 15:00-16:00) by only considering windows whose first record starts at minute 00. Use this helper for morning 07-09 and evening 17-21 windows; then expose best and second-best price values plus their start timestamps in new sensors.

## Implementation Guidance

- **Objectives**: Provide morning/evening window sensors and expose best/second-best (highest) prices plus their start timestamps, ensuring distinct start hours and full-hour windows.
- **Key Tasks**: Add a `find_top_windows()` helper; use it for morning (07-09) and evening (17-21) to select top two windows with distinct start hours; enforce window starts at minute 00; add sensors for best and second-best prices and start timestamps; add translation keys.
- **Dependencies**: Existing `find_optimal_window()` continuity logic; data fields `rce_pln`, `dtime`, `period`; tomorrow availability gate after 14:00.
- **Success Criteria**: Morning window uses 07-09 only and evening uses 17-21 only; best/second-best sensors return highest and second-highest distinct price values with correct start timestamps; tests updated accordingly.

## Research: Method for Selecting Two Best Windows (Morning/Evening)

### Candidate Helper Signature

```python
def find_top_windows(
  data: list[dict],
  window_start_hour: int,
  window_end_hour: int,
  duration_hours: int,
  top_n: int = 2,
  is_max: bool = True,
  distinct_start_hour: bool = True,
) -> list[list[dict]]:
  ...
```

### Algorithm Outline (Derived from `find_optimal_window()`)

1. Filter records whose *period start* hour is within `[window_start_hour, window_end_hour)`.
2. Sort by `dtime` and slide a window of `duration_hours * 4` records.
3. For each candidate window:
   - Enforce 15-minute continuity (same as `find_optimal_window()`).
   - Compute average price from `rce_pln`.
   - Determine window start hour from the first record's `dtime` minus 15 minutes.
  - Skip windows whose start minute is not 00 (full-hour window requirement).
4. Rank candidate windows by average price (descending for `is_max=True`).
5. Select top-N windows, optionally enforcing distinct start hours (to guarantee different hourly windows even if price ties).

### Notes on Distinct Hour Constraint

- If two best windows share the same start hour, skip the later one and pick the next highest with a different start hour.
- The "2nd best" can have the same price as the best, as long as its start hour differs.
- If fewer than two valid windows exist, return one or zero windows accordingly.

### Notes on Full-Hour Windows

- A "full" window is defined as starting at minute 00 and spanning an integer number of hours (e.g., 15:00-16:00).
- Enforce this by checking the computed window start time minute equals 0.

### Output Consumption in Sensors

- Best price: average of the top window; timestamp from its start time.
- 2nd best price: average of the second window; timestamp from its start time.
- Use the same timestamp construction pattern as existing hour-start timestamp sensors.

### Requested New Sensors (today only)

- Morning best price
- Morning best price start timestamp
- Morning 2nd best price
- Morning 2nd best price start timestamp
- Evening best price
- Evening best price start timestamp
- Evening 2nd best price
- Evening 2nd best price start timestamp