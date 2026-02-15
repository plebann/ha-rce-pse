# Home Assistant Custom Component (HACS) Integration Architecture Reference

## Executive Summary

This document provides a comprehensive analysis of the `rce_pse` HACS integration as a reference implementation for well-designed Home Assistant custom components. The integration demonstrates professional-grade architecture with clear separation of concerns, proper inheritance hierarchies, and maintainable code organization.

**Integration Type**: Cloud Polling Service  
**Domain**: `rce_pse`  
**Platforms**: Sensor, Binary Sensor  
**Key Pattern**: DataUpdateCoordinator-based architecture with layered entity classes

---

## Research Executed

### File Analysis

- [manifest.json](custom_components/rce_pse/manifest.json)
  - Standard HACS manifest structure with config_flow support
  - Integration type: `service`, IoT class: `cloud_polling`
  - Minimal external dependencies (aiohttp, async_timeout)

- [__init__.py](custom_components/rce_pse/__init__.py)
  - Clean entry point with proper async lifecycle management
  - Demonstrates coordinator setup and platform forwarding pattern
  - Implements config entry reload on options update

- [coordinator.py](custom_components/rce_pse/coordinator.py)
  - Extends `DataUpdateCoordinator` for centralized data management
  - Implements API fetching, caching, and data processing
  - Handles config options for hourly price averaging

- [shared_base.py](custom_components/rce_pse/shared_base.py)
  - Common base class for all entities (sensors and binary sensors)
  - Provides shared device info, data access methods, and availability logic

- [sensors/base.py](custom_components/rce_pse/sensors/base.py)
  - Sensor-specific base class extending shared base
  - Implements helper methods for price data retrieval and calculations

- [binary_sensors/base.py](custom_components/rce_pse/binary_sensors/base.py)
  - Binary sensor-specific base class
  - Implements window-based time checking logic

- [price_calculator.py](custom_components/rce_pse/price_calculator.py)
  - Pure utility class with static methods
  - Statistical calculations, window optimization, extreme value finding

- [config_flow.py](custom_components/rce_pse/config_flow.py)
  - ConfigFlow and OptionsFlow implementation
  - User-configurable time windows and price calculation options

### Code Search Results

- Entity organization pattern
  - Platform files ([sensor.py](custom_components/rce_pse/sensor.py), [binary_sensor.py](custom_components/rce_pse/binary_sensor.py)) act as entity registries
  - Actual implementations organized in subdirectories ([sensors/](custom_components/rce_pse/sensors/), [binary_sensors/](custom_components/rce_pse/binary_sensors/))
  - `__init__.py` files export all entity classes for clean imports

- Inheritance hierarchy discovered
  - `CoordinatorEntity` (Home Assistant base)
    - `RCEBaseCommonEntity` (shared device/coordinator logic)
      - `RCEBaseSensor` (sensor-specific helpers)
        - Concrete sensor implementations
      - `RCEBaseBinarySensor` (binary sensor-specific helpers)
        - Concrete binary sensor implementations

- Entity categorization by function
  - Main sensors (current price, kWh price)
  - Statistical sensors (avg, min, max, median)
  - Hour timestamp sensors (when min/max occurs)
  - Custom window sensors (cheapest/expensive periods)
  - Binary sensors for window activation states

### Project Structure Conventions

**Directory Layout:**
```
custom_components/
  <domain>/
    __init__.py                    # Integration setup
    const.py                       # Constants and config keys
    coordinator.py                 # Data update coordinator
    config_flow.py                 # UI configuration
    manifest.json                  # Integration metadata
    shared_base.py                 # Common entity base
    price_calculator.py            # Business logic utilities
    sensor.py                      # Sensor platform setup
    binary_sensor.py               # Binary sensor platform setup
    sensors/                       # Sensor implementations
      __init__.py                  # Export all sensors
      base.py                      # Sensor base class
      today_main.py                # Main sensors
      today_stats.py               # Statistical sensors
      today_hours.py               # Hour/timestamp sensors
      custom_windows.py            # Window-based sensors
      tomorrow_*.py                # Tomorrow data sensors
    binary_sensors/                # Binary sensor implementations
      __init__.py                  # Export all binary sensors
      base.py                      # Binary sensor base class
      price_windows.py             # Price-based triggers
      custom_windows.py            # Custom window triggers
```

**File Organization Standards:**
- Platform setup files at root level
- Entity implementations grouped by type in subdirectories
- Business logic separated into utility classes
- Constants centralized in single file
- Base classes provide shared functionality

---

## Key Discoveries

### 1. Data Coordination Architecture

**Pattern**: Single `DataUpdateCoordinator` instance shared across all entities

**Implementation:**
```python
# In __init__.py - Coordinator creation and sharing
coordinator = RCEPSEDataUpdateCoordinator(hass, entry)
await coordinator.async_config_entry_first_refresh()
hass.data[DOMAIN][entry.entry_id] = coordinator

# In sensor.py/binary_sensor.py - Coordinator retrieval
coordinator = hass.data[DOMAIN][config_entry.entry_id]
sensors = [RCETodayMainSensor(coordinator), ...]
```

**Benefits:**
- Single API polling point reduces network calls
- All entities automatically update when coordinator refreshes
- Data consistency across all sensors
- Efficient resource usage

**Coordinator Responsibilities:**
- API communication with error handling
- Data caching with time-based invalidation
- Data transformation (hourly averaging when configured)
- Config option access for data processing

### 2. Inheritance Hierarchy Design

**Four-Layer Architecture:**

```
CoordinatorEntity (Home Assistant)
  └─ RCEBaseCommonEntity (shared_base.py)
      ├─ RCEBaseSensor (sensors/base.py)
      │   ├─ RCETodayStatsSensor (today_stats.py)
      │   │   └─ RCETodayAvgPriceSensor
      │   ├─ RCECustomWindowSensor (custom_windows.py)
      │   │   └─ RCETodayCheapestWindowStartSensor
      │   └─ Direct concrete sensors (today_main.py)
      └─ RCEBaseBinarySensor (binary_sensors/base.py)
          ├─ RCECustomWindowBinarySensor (custom_windows.py)
          │   └─ RCETodayCheapestWindowBinarySensor
          └─ Direct concrete binary sensors (price_windows.py)
```

**Layer 1: CoordinatorEntity** (Home Assistant provided)
- Coordinator integration
- Automatic update handling
- Standard entity lifecycle

**Layer 2: RCEBaseCommonEntity** (shared_base.py)
- Common to both sensors and binary sensors
- Device info configuration
- Data access methods (`get_today_data()`, `get_tomorrow_data()`)
- Tomorrow data availability checking
- Entity availability logic
- Price calculator instance

**Layer 3: Platform-Specific Bases**
- `RCEBaseSensor`: Price retrieval helpers (current, future, past hours)
- `RCEBaseBinarySensor`: Time window checking for binary states

**Layer 4: Category-Specific Bases (Optional)**
- `RCETodayStatsSensor`: Common unit/icon for statistical sensors
- `RCECustomWindowSensor`: Config access for user-defined windows
- `RCECustomWindowBinarySensor`: Config access for binary window sensors

**Layer 5: Concrete Implementations**
- Minimal code, focused on single responsibility
- Override only `native_value` or `is_on` property
- Leverage all inherited functionality

### 3. Entity Organization Patterns

**Subdirectory-Based Grouping:**

Sensors organized by functional category:
- `today_main.py` - Primary current price sensors
- `today_stats.py` - Statistical aggregations (avg, min, max, median)
- `today_hours.py` - Timestamp sensors for price extremes
- `today_prices.py` - Future/past hour price lookups
- `custom_windows.py` - User-configurable time window sensors
- `tomorrow_*.py` - Tomorrow data equivalents

Binary sensors organized by trigger type:
- `price_windows.py` - Automatic min/max price window triggers
- `custom_windows.py` - User-configured window triggers

**Export Pattern:**
```python
# sensors/__init__.py
from .base import RCEBaseSensor
from .today_main import RCETodayMainSensor, RCETodayKwhPriceSensor
from .today_stats import RCETodayAvgPriceSensor, RCETodayMaxPriceSensor
# ... more imports

__all__ = [
    "RCEBaseSensor",
    "RCETodayMainSensor",
    # ... all exported classes
]
```

**Platform Setup Pattern:**
```python
# sensor.py
from .sensors import (
    RCETodayMainSensor,
    RCETodayAvgPriceSensor,
    # ... all needed sensors
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [
        RCETodayMainSensor(coordinator),
        RCETodayAvgPriceSensor(coordinator),
        # ... instantiate all sensors
    ]
    async_add_entities(sensors)
```

### 4. Separation of Business Logic

**Utility Class Pattern** - `PriceCalculator`

Pure static methods, no state, reusable:
```python
class PriceCalculator:
    @staticmethod
    def get_prices_from_data(data: list[dict]) -> list[float]:
        return [float(record["rce_pln"]) for record in data]
    
    @staticmethod
    def calculate_average(prices: list[float]) -> float:
        return sum(prices) / len(prices) if prices else 0.0
    
    @staticmethod
    def find_optimal_window(data, start_hour, end_hour, duration, is_max=False):
        # Complex sliding window algorithm
```

**Benefits:**
- Testable in isolation
- Reusable across sensor types
- No Home Assistant dependencies
- Clear single responsibility

**Usage:**
```python
# In base class
class RCEBaseCommonEntity(CoordinatorEntity):
    def __init__(self, coordinator, unique_id):
        # ...
        self.calculator = PriceCalculator()

# In concrete sensors
prices = self.calculator.get_prices_from_data(today_data)
avg = self.calculator.calculate_average(prices)
```

### 5. Configuration Management

**Two-Level Config System:**

**Initial Setup (`config_flow.py`):**
- `async_step_user()` - Initial integration addition
- Single instance enforcement
- Default values applied

**Options Flow (`config_flow.py`):**
- `async_step_init()` - Options modification UI
- Same schema as initial config
- Triggers integration reload on save

**Config Access Pattern:**
```python
# In coordinator
def _get_config_value(self, key: str, default: any) -> any:
    if not self.config_entry:
        return default
    # Check options first, fallback to initial data
    if self.config_entry.options and key in self.config_entry.options:
        return self.config_entry.options[key]
    elif self.config_entry.data and key in self.config_entry.data:
        return self.config_entry.data.get(key, default)
    return default

# In custom window sensors
def get_config_value(self, key: str, default: any) -> any:
    value = None
    if self.config_entry.options and key in self.config_entry.options:
        value = self.config_entry.options[key]
    else:
        value = self.config_entry.data.get(key, default)
    # Type conversion for numeric configs
    if key in [CONF_WINDOW_START, CONF_WINDOW_END, ...]:
        return int(value)
    return value
```

**Options Update Handling:**
```python
# In __init__.py
async def async_update_options(hass, entry):
    """Reload integration when options change"""
    await hass.config_entries.async_reload(entry.entry_id)
```

### 6. Entity Identification and Translation

**Unique ID Pattern:**
```python
class RCEBaseCommonEntity(CoordinatorEntity):
    def __init__(self, coordinator, unique_id: str):
        super().__init__(coordinator)
        self._attr_unique_id = f"rce_pse_{unique_id}"
        self._attr_has_entity_name = True
        self._attr_translation_key = f"rce_pse_{unique_id}"
```

**Device Grouping:**
```python
@property
def device_info(self):
    return {
        "identifiers": {(DOMAIN, "rce_pse")},
        "name": "RCE PSE",
        "model": "RCE PSE",
        "entry_type": "service",
        "manufacturer": MANUFACTURER,
    }
```

All entities share the same device identifier, grouping them in the UI.

**Translation Files** (`translations/en.json`, `translations/pl.json`):
- Entity names keyed by translation_key
- Supports internationalization
- Clean separation of code and display text

### 7. Data Availability and Update Management

**Availability Logic:**
```python
@property
def available(self) -> bool:
    return (
        self.coordinator.last_update_success
        and self.coordinator.data is not None
        and self.coordinator.data.get("raw_data") is not None
    )
```

**Tomorrow Data Conditional:**
```python
def is_tomorrow_data_available(self) -> bool:
    now = dt_util.now()
    return now.hour >= 14  # Tomorrow prices available after 2 PM
```

**Polling Override for Time-Sensitive Sensors:**
```python
class RCETodayMainSensor(RCEBaseSensor):
    @property
    def should_poll(self) -> bool:
        return True
    
    @property
    def scan_interval(self) -> timedelta:
        return timedelta(minutes=1)  # Faster updates for current price
```

### 8. Error Handling and Resilience

**Coordinator Error Strategy:**
```python
async def _async_update_data(self):
    try:
        async with async_timeout.timeout(30):
            data = await self._fetch_data()
            self._last_api_fetch = now
            return data
    except asyncio.TimeoutError as exception:
        self._last_api_fetch = now
        if self.data:  # Fallback to cached data
            _LOGGER.warning("Using existing data due to API timeout")
            return self.data
        raise UpdateFailed(f"Timeout: {exception}") from exception
```

**Defensive Data Parsing:**
```python
def get_current_price_data(self) -> dict | None:
    for record in self.coordinator.data["raw_data"]:
        try:
            period_end = datetime.strptime(record["dtime"], "%Y-%m-%d %H:%M:%S")
            period_start = period_end - timedelta(minutes=15)
            if period_start <= now <= period_end:
                return record
        except (ValueError, KeyError):
            continue  # Skip malformed records
    return None
```

### 9. Advanced Sensor Patterns

**Sensor with Attributes:**
```python
@property
def extra_state_attributes(self) -> dict[str, Any] | None:
    today_data = self.get_today_data()
    # Filter out sensitive/redundant keys
    excluded_keys = {"rce_pln_neg_to_zero", "publication_ts"}
    sanitized_data = [
        {k: v for k, v in record.items() if k not in excluded_keys}
        for record in today_data
    ]
    return {
        "last_update": self.coordinator.data.get("last_update"),
        "data_points": len(today_data),
        "prices": sanitized_data,
    }
```

**Timestamp Device Class Sensors:**
```python
class RCETodayMinPriceHourStartTimestampSensor(RCEBaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "today_min_price_hour_start_timestamp")
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        # Return datetime object for timestamp sensors
        return window_start  # datetime object
```

**Binary Sensor State Logic:**
```python
@property
def is_on(self) -> bool:
    today_data = self.get_today_data()
    if not today_data:
        return False
    
    # Get optimal window from calculator
    optimal_window = self.calculator.find_optimal_window(
        today_data, start_hour, end_hour, duration, is_max=False
    )
    
    if not optimal_window:
        return False
    
    # Check if current time is in window
    return self.is_current_time_in_window(window_start_str, window_end_str)
```

### 10. Testing Structure

**Test Organization:**
```
tests/
  __init__.py
  conftest.py                 # Shared fixtures
  test_coordinator.py         # Coordinator tests
  test_binary_sensors.py      # Binary sensor tests
  test_sensors_base.py        # Base sensor tests
  test_sensors.py             # Concrete sensor tests
  test_timestamp_sensors.py   # Timestamp sensor tests
  test_integration.py         # Integration tests
```

---

## Implementation Guidance for New Integrations

### Step 1: Foundation Setup

**Directory Structure:**
```
custom_components/<your_domain>/
  __init__.py
  manifest.json
  const.py
  coordinator.py
  config_flow.py
```

**manifest.json Template:**
```json
{
    "domain": "your_domain",
    "name": "Your Integration Name",
    "config_flow": true,
    "documentation": "https://github.com/...",
    "integration_type": "service",
    "iot_class": "cloud_polling",
    "requirements": ["aiohttp>=3.8.0"],
    "version": "1.0.0"
}
```

**const.py Setup:**
```python
from datetime import timedelta
from typing import Final

DOMAIN: Final[str] = "your_domain"
MANUFACTURER: Final[str] = "Your Name"
API_URL: Final[str] = "https://api.example.com"
API_UPDATE_INTERVAL: Final[timedelta] = timedelta(minutes=30)

# Config keys
CONF_YOUR_OPTION: Final[str] = "your_option"
DEFAULT_YOUR_OPTION: Final = "default_value"
```

### Step 2: Data Coordinator Implementation

**Extend DataUpdateCoordinator:**
```python
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

class YourDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config_entry=None):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=API_UPDATE_INTERVAL,
        )
        self.session = None
        self.config_entry = config_entry

    async def _async_update_data(self) -> dict[str, Any]:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        try:
            async with async_timeout.timeout(30):
                data = await self._fetch_data()
                return {
                    "raw_data": data,
                    "last_update": dt_util.now().isoformat(),
                }
        except Exception as exception:
            if self.data:  # Return cached data on error
                _LOGGER.warning("Using cached data due to error")
                return self.data
            raise UpdateFailed(f"Error: {exception}") from exception

    async def _fetch_data(self) -> list[dict]:
        async with self.session.get(API_URL) as response:
            if response.status != 200:
                raise UpdateFailed(f"API returned {response.status}")
            return await response.json()

    async def async_close(self):
        if self.session:
            await self.session.close()
```

### Step 3: Shared Base Entity

**Create shared_base.py:**
```python
from homeassistant.helpers.update_coordinator import CoordinatorEntity

class YourBaseCommonEntity(CoordinatorEntity):
    def __init__(self, coordinator, unique_id: str):
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{unique_id}"
        self._attr_has_entity_name = True
        self._attr_translation_key = f"{DOMAIN}_{unique_id}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, DOMAIN)},
            "name": "Your Integration",
            "manufacturer": MANUFACTURER,
            "entry_type": "service",
        }

    def get_data(self) -> list[dict]:
        if not self.coordinator.data or not self.coordinator.data.get("raw_data"):
            return []
        return self.coordinator.data["raw_data"]

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
        )
```

### Step 4: Platform-Specific Base Classes

**Create sensors/base.py:**
```python
from homeassistant.components.sensor import SensorEntity
from ..shared_base import YourBaseCommonEntity

class YourBaseSensor(YourBaseCommonEntity, SensorEntity):
    def __init__(self, coordinator, unique_id: str):
        super().__init__(coordinator, unique_id)
    
    # Add sensor-specific helper methods
    def calculate_something(self, data):
        # Your logic here
        pass
```

**Create binary_sensors/base.py:**
```python
from homeassistant.components.binary_sensor import BinarySensorEntity
from ..shared_base import YourBaseCommonEntity

class YourBaseBinarySensor(YourBaseCommonEntity, BinarySensorEntity):
    def __init__(self, coordinator, unique_id: str):
        super().__init__(coordinator, unique_id)
    
    # Add binary sensor-specific helper methods
```

### Step 5: Concrete Entity Implementation

**Create sensors/main.py:**
```python
from .base import YourBaseSensor

class YourMainSensor(YourBaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "main_sensor")
        self._attr_native_unit_of_measurement = "units"
        self._attr_icon = "mdi:icon-name"

    @property
    def native_value(self):
        data = self.get_data()
        if not data:
            return None
        # Calculate and return value
        return data[0].get("value")
```

**Create sensors/__init__.py:**
```python
from .base import YourBaseSensor
from .main import YourMainSensor

__all__ = ["YourBaseSensor", "YourMainSensor"]
```

### Step 6: Platform Setup

**Create sensor.py:**
```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .sensors import YourMainSensor

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    sensors = [
        YourMainSensor(coordinator),
        # Add more sensors
    ]
    
    async_add_entities(sensors)
```

### Step 7: Integration Entry Point

**Create __init__.py:**
```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import YourDataUpdateCoordinator

PLATFORMS = ["sensor", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    
    coordinator = YourDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()
    
    return unload_ok
```

### Step 8: Configuration Flow

**Create config_flow.py:**
```python
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_YOUR_OPTION, DEFAULT_YOUR_OPTION

CONFIG_SCHEMA = vol.Schema({
    vol.Optional(CONF_YOUR_OPTION, default=DEFAULT_YOUR_OPTION): str,
})

class YourConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        
        if user_input is not None:
            return self.async_create_entry(
                title="Your Integration",
                data=user_input,
            )
        
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
        )
```

---

## Architectural Patterns Summary

### 1. **Coordinator-Centric Design**
- Single data source for all entities
- Automatic update propagation
- Efficient API usage with caching

### 2. **Layered Inheritance**
- Common base for shared logic
- Platform-specific bases for sensor/binary sensor
- Category-specific bases for related entities
- Minimal concrete implementations

### 3. **Separation of Concerns**
- Business logic in utility classes
- Data fetching in coordinator
- Entity logic in entity classes
- Configuration in config_flow

### 4. **Subdirectory Organization**
- Platform implementations in subdirectories
- Related entities grouped by function
- Clean export pattern via `__init__.py`

### 5. **Type Safety and Modern Python**
- Type hints throughout
- `from __future__ import annotations` for forward compatibility
- `TYPE_CHECKING` for circular import prevention
- Final constants with type annotations

### 6. **Error Resilience**
- Graceful degradation to cached data
- Defensive parsing with try/except
- Comprehensive error logging
- None-safe return values

### 7. **Configurability**
- Config flow for initial setup
- Options flow for runtime changes
- Config access helpers in base classes
- Reload on configuration change

### 8. **Entity Best Practices**
- Unique IDs for persistence
- Device grouping for UI organization
- Translation keys for internationalization
- Proper device classes for specialized sensors
- Availability checking

---

## Code Quality Indicators

### What Makes This a Well-Designed Integration

1. **DRY Principle**: No code duplication, shared logic in base classes
2. **Single Responsibility**: Each class has one clear purpose
3. **Open/Closed**: Easy to add new sensors without modifying existing code
4. **Dependency Injection**: Coordinator passed to entities, testable
5. **Defensive Programming**: Null checks, error handling, fallbacks
6. **Type Safety**: Comprehensive type hints
7. **Documentation**: Clear comments, logging, structured code
8. **Scalability**: Easy to add new sensor types, can support many sensors
9. **Maintainability**: Clear file organization, consistent patterns
10. **Performance**: Caching, single API polling point, efficient updates

### Key Takeaways for Your Integration

1. **Start with coordinator** - Build your data fetching foundation first
2. **Create shared base** - Put common logic in one place
3. **Plan inheritance** - Think about sensor categories and shared functionality
4. **Separate business logic** - Use utility classes for calculations
5. **Organize by function** - Group related entities in subdirectories
6. **Export cleanly** - Use `__init__.py` for clean imports
7. **Handle errors** - Fallback to cached data, defensive parsing
8. **Support configuration** - Config flow + options flow pattern
9. **Test thoroughly** - Structure tests matching code organization
10. **Document well** - Clear naming, type hints, comments

---

## Refactoring Existing Integrations

This section provides guidance for restructuring an existing Home Assistant integration to follow the architectural patterns demonstrated in this reference implementation.

### Pre-Refactoring Assessment

**Analyze your current integration using this checklist:**

#### 1. Data Management Assessment
- [ ] Are entities fetching data independently? (Need coordinator)
- [ ] Is the same API called multiple times? (Need coordinator)
- [ ] Are updates inconsistent across entities? (Need coordinator)
- [ ] Is data processing scattered across multiple files? (Need centralization)

#### 2. Code Organization Assessment
- [ ] Are all entity classes in single large files? (Need subdirectory structure)
- [ ] Is there duplicate code across similar entities? (Need base classes)
- [ ] Are business logic and entity logic mixed? (Need separation)
- [ ] Do entities access config_entry directly? (Need helper methods)

#### 3. Inheritance Assessment
- [ ] Do entities inherit directly from SensorEntity/BinarySensorEntity? (Need base layers)
- [ ] Is there copy-pasted code for device_info? (Need common base)
- [ ] Do similar sensors repeat the same initialization? (Need category bases)
- [ ] Are helper methods duplicated? (Need base class extraction)

#### 4. Configuration Assessment
- [ ] Is configuration hardcoded? (Need config flow)
- [ ] Can users change settings after setup? (Need options flow)
- [ ] Are default values scattered across files? (Need const.py)
- [ ] Does config change require manual restart? (Need reload logic)

**Assessment Outcome:**
- **0-5 issues**: Minor cleanup recommended
- **6-10 issues**: Moderate refactoring beneficial
- **11+ issues**: Major restructuring recommended

### Incremental Migration Strategy

**Never refactor everything at once.** Follow this phased approach:

---

#### Phase 1: Extract Constants (Low Risk)

**Goal:** Centralize all configuration values and constants

**Steps:**
1. Create `const.py` if it doesn't exist
2. Move all hardcoded values to constants
3. Use `Final` type hints for immutability

**Before:**
```python
# sensor.py
API_URL = "https://api.example.com"
UPDATE_INTERVAL = 30  # minutes

class MySensor(SensorEntity):
    def __init__(self):
        self._update_interval = timedelta(minutes=30)
```

**After:**
```python
# const.py
from datetime import timedelta
from typing import Final

DOMAIN: Final[str] = "my_integration"
API_URL: Final[str] = "https://api.example.com"
UPDATE_INTERVAL: Final[timedelta] = timedelta(minutes=30)

# sensor.py
from .const import UPDATE_INTERVAL

class MySensor(SensorEntity):
    def __init__(self):
        self._update_interval = UPDATE_INTERVAL
```

**Testing:** Verify all entities still function after constant extraction

---

#### Phase 2: Implement Data Coordinator (Medium Risk)

**Goal:** Centralize data fetching and eliminate redundant API calls

**Steps:**
1. Create `coordinator.py` with DataUpdateCoordinator
2. Move all API fetching logic to coordinator
3. Update `__init__.py` to create and share coordinator
4. Gradually migrate entities to use coordinator data

**Before:**
```python
# sensor.py
class MySensor(SensorEntity):
    async def async_update(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                self._data = await response.json()
```

**After:**
```python
# coordinator.py
class MyDataUpdateCoordinator(DataUpdateCoordinator):
    async def _async_update_data(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        async with self.session.get(API_URL) as response:
            return await response.json()

# __init__.py
async def async_setup_entry(hass, entry):
    coordinator = MyDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

# sensor.py
class MySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
    
    @property
    def native_value(self):
        return self.coordinator.data.get("value")
```

**Migration Strategy:**
- Convert one entity first as proof of concept
- Verify it works correctly
- Migrate remaining entities in small batches
- Remove old `async_update()` methods

**Testing:** Monitor API calls to confirm single polling point

---

#### Phase 3: Extract Common Base Class (Medium Risk)

**Goal:** Eliminate duplicate device_info, initialization, and availability logic

**Steps:**
1. Create `shared_base.py`
2. Identify code common to ALL entities
3. Create base class extending CoordinatorEntity
4. Migrate entities to inherit from new base

**Before:**
```python
# Multiple sensor files with duplicate code
class Sensor1(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_sensor1"
        self._attr_has_entity_name = True
    
    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, DOMAIN)}, ...}
    
    @property
    def available(self):
        return self.coordinator.last_update_success

class Sensor2(CoordinatorEntity, SensorEntity):
    # Same device_info, available, initialization...
```

**After:**
```python
# shared_base.py
class MyBaseCommonEntity(CoordinatorEntity):
    def __init__(self, coordinator, unique_id: str):
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{unique_id}"
        self._attr_has_entity_name = True
    
    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, DOMAIN)}, ...}
    
    @property
    def available(self):
        return self.coordinator.last_update_success

# sensor files
class Sensor1(MyBaseCommonEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator, "sensor1")
```

**Testing:** Verify device grouping and entity availability unchanged

---

#### Phase 4: Create Platform-Specific Bases (Low Risk)

**Goal:** Extract sensor-specific and binary sensor-specific helper methods

**Steps:**
1. Create `sensors/base.py` and `binary_sensors/base.py`
2. Move sensor-specific helpers to appropriate base
3. Update entities to inherit from platform bases

**Before:**
```python
# Multiple sensors with duplicate helper methods
class Sensor1(MyBaseCommonEntity, SensorEntity):
    def get_value_from_data(self, key):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(key)

class Sensor2(MyBaseCommonEntity, SensorEntity):
    def get_value_from_data(self, key):  # Duplicate!
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(key)
```

**After:**
```python
# sensors/base.py
class MyBaseSensor(MyBaseCommonEntity, SensorEntity):
    def __init__(self, coordinator, unique_id: str):
        super().__init__(coordinator, unique_id)
    
    def get_value_from_data(self, key):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(key)

# sensor files
class Sensor1(MyBaseSensor):
    @property
    def native_value(self):
        return self.get_value_from_data("key1")
```

**Testing:** Verify all sensor helpers still accessible

---

#### Phase 5: Reorganize into Subdirectories (Low Risk)

**Goal:** Improve maintainability through logical file organization

**Steps:**
1. Create `sensors/` and `binary_sensors/` directories
2. Create category-based files (main.py, stats.py, etc.)
3. Move entities to appropriate files
4. Create `__init__.py` with exports
5. Update platform files to import from new locations

**Before:**
```python
# All in sensor.py (500+ lines)
class Sensor1(MyBaseSensor): ...
class Sensor2(MyBaseSensor): ...
class Sensor3(MyBaseSensor): ...
# ... 20 more sensors
```

**After:**
```python
# sensors/main.py
class Sensor1(MyBaseSensor): ...

# sensors/stats.py  
class Sensor2(MyBaseSensor): ...
class Sensor3(MyBaseSensor): ...

# sensors/__init__.py
from .main import Sensor1
from .stats import Sensor2, Sensor3
__all__ = ["Sensor1", "Sensor2", "Sensor3"]

# sensor.py
from .sensors import Sensor1, Sensor2, Sensor3
```

**Migration Strategy:**
- Move one category at a time
- Test after each category moved
- Update imports incrementally

**Testing:** Verify all entities still load correctly

---

#### Phase 6: Extract Business Logic (Medium Risk)

**Goal:** Separate calculations and algorithms from entity code

**Steps:**
1. Identify calculation logic in entities
2. Create utility class (e.g., `calculator.py`)
3. Implement as static methods
4. Replace inline calculations with utility calls

**Before:**
```python
class AvgSensor(MyBaseSensor):
    @property
    def native_value(self):
        data = self.coordinator.data.get("values", [])
        if not data:
            return None
        return sum(data) / len(data)  # Calculation mixed with entity

class MedianSensor(MyBaseSensor):
    @property
    def native_value(self):
        data = self.coordinator.data.get("values", [])
        if not data:
            return None
        sorted_data = sorted(data)
        n = len(sorted_data)
        return sorted_data[n // 2]  # Another calculation
```

**After:**
```python
# calculator.py
class DataCalculator:
    @staticmethod
    def calculate_average(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0
    
    @staticmethod
    def calculate_median(values: list[float]) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        return sorted_values[n // 2]

# sensors
class AvgSensor(MyBaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "avg")
        self.calculator = DataCalculator()
    
    @property
    def native_value(self):
        data = self.coordinator.data.get("values", [])
        return self.calculator.calculate_average(data)
```

**Benefits:**
- Business logic testable in isolation
- Reusable across multiple entities
- Clearer separation of concerns

**Testing:** Unit test calculator methods separately

---

#### Phase 7: Add Category-Specific Bases (Optional, Low Risk)

**Goal:** Further reduce code in similar entity groups

**Steps:**
1. Identify groups of entities with common patterns
2. Create intermediate base classes
3. Move common initialization to base

**Before:**
```python
class AvgSensor(MyBaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "avg")
        self._attr_native_unit_of_measurement = "units"
        self._attr_icon = "mdi:chart-line"

class MaxSensor(MyBaseSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "max")
        self._attr_native_unit_of_measurement = "units"  # Duplicate
        self._attr_icon = "mdi:chart-line"  # Duplicate
```

**After:**
```python
class MyStatsSensor(MyBaseSensor):
    def __init__(self, coordinator, unique_id: str):
        super().__init__(coordinator, unique_id)
        self._attr_native_unit_of_measurement = "units"
        self._attr_icon = "mdi:chart-line"

class AvgSensor(MyStatsSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator, "avg")
    
    @property
    def native_value(self):
        # Only unique logic here
```

**Testing:** Verify units and icons display correctly

---

### Before/After Comparison Examples

#### Example 1: Flat Structure → Organized Structure

**Before (Flat):**
```
custom_components/my_integration/
  __init__.py
  sensor.py (800 lines, 25 sensors)
  binary_sensor.py (300 lines, 5 binary sensors)
  const.py
```

**After (Organized):**
```
custom_components/my_integration/
  __init__.py
  const.py
  coordinator.py
  shared_base.py
  calculator.py
  config_flow.py
  sensor.py (50 lines, setup only)
  binary_sensor.py (30 lines, setup only)
  sensors/
    __init__.py
    base.py
    main.py (2 sensors)
    stats.py (5 sensors)
    hourly.py (8 sensors)
    custom.py (10 sensors)
  binary_sensors/
    __init__.py
    base.py
    windows.py (3 sensors)
    triggers.py (2 sensors)
```

#### Example 2: Direct Inheritance → Layered Inheritance

**Before:**
```python
# All sensors inherit directly from platform classes
class CurrentPriceSensor(CoordinatorEntity, SensorEntity):
    # 50 lines of code
    pass

class AvgPriceSensor(CoordinatorEntity, SensorEntity):
    # 45 lines with duplicate device_info, availability, etc.
    pass
```

**After:**
```python
# Layered inheritance eliminates duplication
CoordinatorEntity
  └─ MyBaseCommonEntity (shared_base.py) - 20 lines
      └─ MyBaseSensor (sensors/base.py) - 15 lines
          └─ MyStatsSensor (sensors/stats.py) - 10 lines
              ├─ CurrentPriceSensor - 8 lines
              └─ AvgPriceSensor - 10 lines
```

#### Example 3: Individual Updates → Coordinator Updates

**Before:**
```python
# Each sensor fetches independently (N API calls)
class Sensor1(SensorEntity):
    async def async_update(self):
        self._data = await fetch_from_api()  # API call 1

class Sensor2(SensorEntity):
    async def async_update(self):
        self._data = await fetch_from_api()  # API call 2 (duplicate!)
```

**After:**
```python
# Single coordinator fetches once (1 API call)
class MyCoordinator(DataUpdateCoordinator):
    async def _async_update_data(self):
        return await fetch_from_api()  # Single API call

# All sensors use shared data
class Sensor1(CoordinatorEntity, SensorEntity):
    @property
    def native_value(self):
        return self.coordinator.data.get("value1")
```

---

### Migration Priority Order

**Follow this sequence for safest refactoring:**

| Phase | Risk | Impact | Effort | Priority |
|-------|------|--------|--------|----------|
| 1. Extract Constants | Low | Low | Low | Do First |
| 2. Implement Coordinator | Medium | High | Medium | Do Second |
| 3. Common Base Class | Medium | Medium | Low | Do Third |
| 4. Platform Bases | Low | Medium | Low | Do Fourth |
| 5. Subdirectory Reorganization | Low | Low | Medium | Do Fifth |
| 6. Extract Business Logic | Medium | Medium | Medium | Do Sixth |
| 7. Category Bases | Low | Low | Low | Optional |

**Why This Order?**
1. Constants are safest, provide immediate cleanup
2. Coordinator provides biggest efficiency gain
3. Base classes reduce duplication significantly
4. Organization improves long-term maintainability
5. Business logic extraction enables better testing

---

### Testing Strategy During Refactoring

#### 1. Baseline Testing (Before Starting)

**Establish current behavior:**
```python
# Create test file documenting current behavior
def test_current_sensor_values():
    """Record current values for comparison after refactoring"""
    assert sensor1.state == expected_value_1
    assert sensor2.state == expected_value_2
    # Document ALL current behaviors
```

#### 2. Unit Tests for New Components

**Test new code in isolation:**
```python
# Test coordinator
async def test_coordinator_fetch():
    coordinator = MyCoordinator(hass)
    await coordinator.async_refresh()
    assert coordinator.data is not None

# Test calculator
def test_calculator_average():
    result = MyCalculator.calculate_average([1, 2, 3])
    assert result == 2.0
```

#### 3. Integration Tests After Each Phase

**Verify entities still work:**
```python
async def test_entities_load():
    """Ensure all entities load after refactoring"""
    await async_setup_entry(hass, config_entry)
    entities = hass.states.async_all()
    assert len(entities) == expected_count

async def test_sensor_values_unchanged():
    """Verify values match pre-refactoring baseline"""
    await async_setup_entry(hass, config_entry)
    assert hass.states.get("sensor.my_sensor_1").state == baseline_value_1
```

#### 4. Manual Testing Checklist

After each phase, manually verify:
- [ ] Integration loads without errors
- [ ] All entities appear in UI
- [ ] Entities grouped under correct device
- [ ] Values update correctly
- [ ] Configuration options work
- [ ] Reloading integration works
- [ ] No error logs in Home Assistant

---

### Common Refactoring Pitfalls

#### Pitfall 1: Breaking Changes to Unique IDs

**Problem:** Changing unique_id breaks existing entities for users

**Bad:**
```python
# Before
self._attr_unique_id = "sensor_1"

# After refactoring (BREAKS USERS!)
self._attr_unique_id = f"{DOMAIN}_sensor_1"
```

**Solution:** Keep unique_ids unchanged or provide migration
```python
# Option 1: Keep original format
self._attr_unique_id = "sensor_1"  # Don't change

# Option 2: Add migration code in __init__.py
async def async_migrate_entry(hass, config_entry):
    """Migrate old unique IDs to new format"""
```

#### Pitfall 2: Forgetting to Close Sessions

**Problem:** Creating coordinator but not cleaning up

**Bad:**
```python
class MyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass):
        self.session = aiohttp.ClientSession()
    # No cleanup!
```

**Solution:** Implement cleanup
```python
class MyCoordinator(DataUpdateCoordinator):
    async def async_close(self):
        if self.session:
            await self.session.close()

# In __init__.py
async def async_unload_entry(hass, entry):
    coordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.async_close()  # Clean up
```

#### Pitfall 3: Circular Imports

**Problem:** Base class imports from entity files that import base

**Bad:**
```python
# base.py
from .stats import calculate_avg  # Circular!

# stats.py
from .base import MyBaseSensor  # Circular!
```

**Solution:** Use TYPE_CHECKING and extract utilities
```python
# calculator.py (separate file)
class Calculator:
    @staticmethod
    def calculate_avg(data):
        pass

# base.py
from .calculator import Calculator

# stats.py
from .base import MyBaseSensor
```

#### Pitfall 4: Over-Engineering Too Soon

**Problem:** Creating too many abstraction layers prematurely

**Bad:**
```python
# 5 sensors don't need 7 base classes
BaseEntity → CommonBase → PlatformBase → CategoryBase → 
  SubCategoryBase → TypeBase → ConcreteEntity
```

**Solution:** Start simple, add layers only when duplication appears
```python
# 5 sensors need 2-3 layers maximum
CoordinatorEntity → CommonBase → PlatformBase → ConcreteEntity
```

#### Pitfall 5: Breaking Backward Compatibility

**Problem:** Removing config options users depend on

**Bad:**
```python
# Removed CONF_OLD_OPTION entirely
# Users' configurations break
```

**Solution:** Deprecate gracefully with fallback
```python
# Support old config with warning
if CONF_OLD_OPTION in config:
    _LOGGER.warning("CONF_OLD_OPTION deprecated, use CONF_NEW_OPTION")
    config[CONF_NEW_OPTION] = config[CONF_OLD_OPTION]
```

#### Pitfall 6: Not Testing with Real Home Assistant

**Problem:** Unit tests pass but integration fails in HA

**Solution:** Test in actual Home Assistant instance
```bash
# Copy to HA custom_components after each phase
cp -r custom_components/my_integration /path/to/homeassistant/custom_components/
# Restart HA and verify in UI
```

---

### Refactoring Checklist

Use this checklist to track your refactoring progress:

#### Preparation
- [ ] Document current entity unique IDs (preserve these!)
- [ ] Create baseline test suite with current behaviors
- [ ] Back up current working code (git branch)
- [ ] Set up testing Home Assistant instance

#### Phase 1: Constants
- [ ] Created const.py with Final type hints
- [ ] Moved all hardcoded values to constants
- [ ] Updated all files to import from const
- [ ] Verified entities still work

#### Phase 2: Coordinator
- [ ] Created coordinator.py extending DataUpdateCoordinator
- [ ] Moved API fetching to coordinator
- [ ] Updated __init__.py to create coordinator
- [ ] Migrated entities to CoordinatorEntity
- [ ] Added async_close() cleanup
- [ ] Verified single API polling
- [ ] Confirmed all entities update together

#### Phase 3: Common Base
- [ ] Created shared_base.py
- [ ] Extracted common device_info
- [ ] Extracted common initialization
- [ ] Extracted common availability logic
- [ ] Migrated all entities to new base
- [ ] Verified device grouping unchanged

#### Phase 4: Platform Bases
- [ ] Created sensors/base.py
- [ ] Created binary_sensors/base.py
- [ ] Extracted platform-specific helpers
- [ ] Migrated entities to platform bases
- [ ] Verified all helpers accessible

#### Phase 5: Organization
- [ ] Created sensors/ directory
- [ ] Created binary_sensors/ directory
- [ ] Organized entities into logical files
- [ ] Created __init__.py exports
- [ ] Updated platform files
- [ ] Verified all entities load

#### Phase 6: Business Logic
- [ ] Created utility class file
- [ ] Extracted calculations to static methods
- [ ] Replaced inline calculations
- [ ] Added unit tests for utilities
- [ ] Verified calculations correct

#### Phase 7: Category Bases (Optional)
- [ ] Identified entity groups
- [ ] Created category base classes
- [ ] Migrated entity groups
- [ ] Verified common properties correct

#### Final Verification
- [ ] All entities appear in UI
- [ ] All unique IDs unchanged
- [ ] All values calculate correctly
- [ ] Configuration still works
- [ ] Reload works properly
- [ ] No errors in logs
- [ ] Performance improved
- [ ] Code more maintainable

---

## Recommended Approach

**For a new integration, follow this architecture:**

1. **Foundation Layer**
   - Manifest and constants
   - DataUpdateCoordinator with API fetching
   - Config flow for user setup

2. **Base Entity Layer**
   - Shared base class extending CoordinatorEntity
   - Platform-specific bases (sensor, binary sensor)
   - Common data access and device info methods

3. **Business Logic Layer**
   - Utility classes with static methods
   - Data processing and calculations
   - Keep separate from Home Assistant entities

4. **Entity Implementation Layer**
   - Organize in subdirectories by function
   - One file per entity group
   - Minimal code, leverage base classes
   - Export via `__init__.py`

5. **Platform Setup Layer**
   - Platform files (sensor.py, binary_sensor.py)
   - Import and instantiate entities
   - Register with Home Assistant

6. **Integration Entry Layer**
   - `__init__.py` lifecycle management
   - Platform forwarding
   - Options update handling

**This architecture provides:**
- Excellent maintainability through clear organization
- Easy extensibility by adding new entity files
- Strong testability with separated concerns
- Professional code quality through consistent patterns
- Efficient resource usage via coordinator pattern
