from __future__ import annotations

from datetime import timedelta
from unittest.mock import Mock

import pytest
import voluptuous as vol
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.rce_prices import (
    SERVICE_FIND_CHEAPEST_WINDOW_SCHEMA,
    _async_handle_find_cheapest_window,
    async_setup,
)
from custom_components.rce_prices.const import (
    ATTR_DURATION_HOURS,
    ATTR_END_HOUR,
    ATTR_START_HOUR,
    DEFAULT_SERVICE_END_HOUR,
    DEFAULT_SERVICE_START_HOUR,
    DOMAIN,
    SERVICE_FIND_CHEAPEST_WINDOW,
)


def _build_quarter_record(today: str, hour: int, minute: int, price: float) -> dict:
    period_start = f"{hour:02d}:{minute:02d}"
    end_hour = hour
    end_minute = minute + 15
    if end_minute >= 60:
        end_hour += 1
        end_minute -= 60

    return {
        "dtime": f"{today} {end_hour:02d}:{end_minute:02d}:00",
        "period": f"{period_start} - {end_hour:02d}:{end_minute:02d}",
        "rce_pln": f"{price:.2f}",
        "business_date": today,
        "publication_ts": f"{today}T23:00:00Z",
    }


def _build_today_quarter_data() -> list[dict]:
    today = dt_util.now().strftime("%Y-%m-%d")
    records: list[dict] = []

    prices_by_hour = {
        8: [100.0, 110.0, 120.0, 130.0],
        9: [200.0, 210.0, 220.0, 230.0],
        10: [50.0, 60.0, 70.0, 80.0],
        11: [90.0, 100.0, 110.0, 120.0],
    }

    for hour, prices in prices_by_hour.items():
        for index, price in enumerate(prices):
            minute = index * 15
            records.append(_build_quarter_record(today, hour, minute, price))

    return records


class TestFindCheapestWindowService:
    @pytest.mark.asyncio
    async def test_async_setup_registers_service(self, mock_hass):
        mock_hass.services = Mock()
        mock_hass.services.has_service = Mock(return_value=False)
        mock_hass.services.async_register = Mock()

        result = await async_setup(mock_hass, {})

        assert result is True
        mock_hass.services.async_register.assert_called_once()
        args, kwargs = mock_hass.services.async_register.call_args
        assert args[0] == DOMAIN
        assert args[1] == SERVICE_FIND_CHEAPEST_WINDOW
        assert kwargs["supports_response"] == SupportsResponse.ONLY

    def test_service_schema_defaults(self):
        validated = SERVICE_FIND_CHEAPEST_WINDOW_SCHEMA({ATTR_DURATION_HOURS: 2})

        assert validated[ATTR_DURATION_HOURS] == 2
        assert validated[ATTR_START_HOUR] == DEFAULT_SERVICE_START_HOUR
        assert validated[ATTR_END_HOUR] == DEFAULT_SERVICE_END_HOUR

    def test_service_schema_rejects_fractional_duration(self):
        with pytest.raises(vol.Invalid):
            SERVICE_FIND_CHEAPEST_WINDOW_SCHEMA({ATTR_DURATION_HOURS: 1.5})

    @pytest.mark.asyncio
    async def test_handler_returns_hourly_averages(self, mock_hass):
        coordinator = Mock()
        coordinator.data = {"raw_data": _build_today_quarter_data()}
        mock_hass.data[DOMAIN] = {"entry_1": coordinator}

        call = Mock()
        call.data = {
            ATTR_DURATION_HOURS: 2,
            ATTR_START_HOUR: 8,
            ATTR_END_HOUR: 16,
        }

        response = await _async_handle_find_cheapest_window(mock_hass, call)

        assert response["average_price"] == 85.0
        assert len(response["prices"]) == 2
        assert response["prices"][0]["price"] == 65.0
        assert response["prices"][1]["price"] == 105.0
        assert "T10:00:00" in response["start"]
        assert "T12:00:00" in response["end"]

    @pytest.mark.asyncio
    async def test_handler_raises_when_no_coordinator(self, mock_hass):
        mock_hass.data[DOMAIN] = {}

        call = Mock()
        call.data = {
            ATTR_DURATION_HOURS: 2,
            ATTR_START_HOUR: 8,
            ATTR_END_HOUR: 16,
        }

        with pytest.raises(ServiceValidationError):
            await _async_handle_find_cheapest_window(mock_hass, call)

    @pytest.mark.asyncio
    async def test_handler_raises_when_duration_does_not_fit(self, mock_hass):
        coordinator = Mock()
        coordinator.data = {"raw_data": _build_today_quarter_data()}
        mock_hass.data[DOMAIN] = {"entry_1": coordinator}

        call = Mock()
        call.data = {
            ATTR_DURATION_HOURS: 4,
            ATTR_START_HOUR: 8,
            ATTR_END_HOUR: 10,
        }

        with pytest.raises(ServiceValidationError):
            await _async_handle_find_cheapest_window(mock_hass, call)