from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_DURATION_HOURS,
    ATTR_END_HOUR,
    ATTR_START_HOUR,
    DEFAULT_SERVICE_END_HOUR,
    DEFAULT_SERVICE_START_HOUR,
    DOMAIN,
    MAX_SERVICE_DURATION_HOURS,
    MIN_SERVICE_DURATION_HOURS,
    SERVICE_FIND_CHEAPEST_WINDOW,
)
from .coordinator import RCEPSEDataUpdateCoordinator
from .price_calculator import PriceCalculator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def _validate_duration_hours(value: Any) -> int:
    if isinstance(value, bool):
        raise vol.Invalid("Duration must be a full number of hours")

    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    raise vol.Invalid("Duration must be a full number of hours")


SERVICE_FIND_CHEAPEST_WINDOW_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DURATION_HOURS): vol.All(
            _validate_duration_hours,
            vol.Range(min=MIN_SERVICE_DURATION_HOURS, max=MAX_SERVICE_DURATION_HOURS),
        ),
        vol.Optional(ATTR_START_HOUR, default=DEFAULT_SERVICE_START_HOUR): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=23)
        ),
        vol.Optional(ATTR_END_HOUR, default=DEFAULT_SERVICE_END_HOUR): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=24)
        ),
    }
)


def _format_local_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
    return dt_util.as_local(value).isoformat()


async def _async_handle_find_cheapest_window(
    hass: HomeAssistant, call: ServiceCall
) -> ServiceResponse:
    duration_hours = call.data[ATTR_DURATION_HOURS]
    start_hour = call.data[ATTR_START_HOUR]
    end_hour = call.data[ATTR_END_HOUR]

    if start_hour >= end_hour:
        raise ServiceValidationError("start_hour must be lower than end_hour")

    if duration_hours > (end_hour - start_hour):
        raise ServiceValidationError(
            "duration_hours must fit between start_hour and end_hour"
        )

    coordinators = hass.data.get(DOMAIN, {})
    if not coordinators:
        raise ServiceValidationError("No loaded RCE Prices config entry")

    coordinator = next(iter(coordinators.values()))
    raw_data = coordinator.data.get("raw_data") if coordinator.data else None
    if not raw_data:
        raise ServiceValidationError("No RCE Prices data available")

    today = dt_util.now().strftime("%Y-%m-%d")
    today_data = [record for record in raw_data if record.get("business_date") == today]
    if not today_data:
        raise ServiceValidationError("No RCE Prices data for today")

    window = PriceCalculator.find_optimal_window(
        today_data,
        start_hour,
        end_hour,
        duration_hours,
        is_max=False,
    )
    if not window:
        raise ServiceValidationError("No matching price window found")

    hourly_prices: dict[datetime, list[float]] = {}
    all_prices: list[float] = []

    for record in window:
        try:
            period_end = datetime.strptime(record["dtime"], "%Y-%m-%d %H:%M:%S")
            period_start = period_end - timedelta(minutes=15)
            hour_start = period_start.replace(minute=0, second=0, microsecond=0)

            hourly_prices.setdefault(hour_start, []).append(float(record["rce_pln"]))
            all_prices.append(float(record["rce_pln"]))
        except (ValueError, KeyError):
            continue

    if not hourly_prices or not all_prices:
        raise ServiceValidationError("No valid prices in selected window")

    hour_starts = sorted(hourly_prices)
    hourly_response = []
    for hour_start in hour_starts:
        hour_end = hour_start + timedelta(hours=1)
        hour_average = round(sum(hourly_prices[hour_start]) / len(hourly_prices[hour_start]), 2)
        hourly_response.append(
            {
                "start": _format_local_datetime(hour_start),
                "end": _format_local_datetime(hour_end),
                "price": hour_average,
            }
        )

    window_start = hour_starts[0]
    window_end = hour_starts[-1] + timedelta(hours=1)
    total_average = round(sum(all_prices) / len(all_prices), 2)

    return {
        "start": _format_local_datetime(window_start),
        "end": _format_local_datetime(window_end),
        "average_price": total_average,
        "prices": hourly_response,
    }


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    _LOGGER.debug("Setting up RCE Prices integration")
    hass.data.setdefault(DOMAIN, {})

    if not hass.services.has_service(DOMAIN, SERVICE_FIND_CHEAPEST_WINDOW):

        async def async_handle_find_cheapest_window(call: ServiceCall) -> ServiceResponse:
            return await _async_handle_find_cheapest_window(hass, call)

        hass.services.async_register(
            DOMAIN,
            SERVICE_FIND_CHEAPEST_WINDOW,
            async_handle_find_cheapest_window,
            schema=SERVICE_FIND_CHEAPEST_WINDOW_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    _LOGGER.debug("RCE Prices integration setup completed")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("Setting up RCE Prices config entry: %s", entry.entry_id)
    hass.data.setdefault(DOMAIN, {})
    
    coordinator = RCEPSEDataUpdateCoordinator(hass, entry)
    _LOGGER.debug("Created data coordinator for RCE Prices")
    
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("Completed first data refresh for RCE Prices")
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.debug("RCE Prices config entry setup completed successfully")
    
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    _LOGGER.debug("Options updated for RCE Prices, reloading entry: %s", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("Unloading RCE Prices config entry: %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()
        _LOGGER.debug("RCE Prices config entry unloaded successfully")
    else:
        _LOGGER.warning("Failed to unload RCE Prices config entry: %s", entry.entry_id)
    
    return unload_ok 