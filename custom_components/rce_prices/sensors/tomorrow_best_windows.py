from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.util import dt as dt_util

from .base import RCEBaseSensor
from ..const import (
    BEST_WINDOW_DURATION_HOURS,
    EVENING_BEST_WINDOW_END_HOUR,
    EVENING_BEST_WINDOW_START_HOUR,
    MORNING_BEST_WINDOW_END_HOUR,
    MORNING_BEST_WINDOW_START_HOUR,
)

if TYPE_CHECKING:
    from ..coordinator import RCEPSEDataUpdateCoordinator


class RCETomorrowBestWindowSensor(RCEBaseSensor):
    """Base sensor for tomorrow best window calculations."""

    def __init__(
        self,
        coordinator: RCEPSEDataUpdateCoordinator,
        unique_id: str,
        window_start_hour: int,
        window_end_hour: int,
        window_rank: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id)
        self._window_start_hour = window_start_hour
        self._window_end_hour = window_end_hour
        self._window_rank = window_rank

    def _get_window(self) -> list[dict] | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None

        windows = self.calculator.find_top_windows(
            tomorrow_data,
            self._window_start_hour,
            self._window_end_hour,
            BEST_WINDOW_DURATION_HOURS,
            top_n=self._window_rank + 1,
            is_max=True,
            distinct_start_hour=True,
        )

        if len(windows) <= self._window_rank:
            return None

        return windows[self._window_rank]

    def _get_window_start(self, window: list[dict]) -> datetime | None:
        try:
            first_period_end = datetime.strptime(window[0]["dtime"], "%Y-%m-%d %H:%M:%S")
            window_start = first_period_end - timedelta(minutes=15)
            return dt_util.as_local(window_start)
        except (ValueError, KeyError, IndexError):
            return None


class RCETomorrowBestWindowPriceSensor(RCETomorrowBestWindowSensor):
    """Base sensor for tomorrow best window price outputs."""

    def __init__(
        self,
        coordinator: RCEPSEDataUpdateCoordinator,
        unique_id: str,
        window_start_hour: int,
        window_end_hour: int,
        window_rank: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id, window_start_hour, window_end_hour, window_rank)
        self._attr_native_unit_of_measurement = "PLN/MWh"
        self._attr_icon = "mdi:cash"

    @property
    def native_value(self) -> float | None:
        window = self._get_window()
        if not window:
            return None

        try:
            prices = [float(record["rce_pln"]) for record in window]
        except (ValueError, KeyError):
            return None

        return round(self.calculator.calculate_average(prices), 2)


class RCETomorrowBestWindowStartTimestampSensor(RCETomorrowBestWindowSensor):
    """Base sensor for tomorrow best window start timestamps."""

    def __init__(
        self,
        coordinator: RCEPSEDataUpdateCoordinator,
        unique_id: str,
        window_start_hour: int,
        window_end_hour: int,
        window_rank: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, unique_id, window_start_hour, window_end_hour, window_rank)
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-start"

    @property
    def native_value(self) -> datetime | None:
        window = self._get_window()
        if not window:
            return None

        return self._get_window_start(window)


class RCETomorrowMorningBestPriceSensor(RCETomorrowBestWindowPriceSensor):
    """Tomorrow morning best price (highest) sensor."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tomorrow_morning_best_price",
            MORNING_BEST_WINDOW_START_HOUR,
            MORNING_BEST_WINDOW_END_HOUR,
            0,
        )


class RCETomorrowMorningSecondBestPriceSensor(RCETomorrowBestWindowPriceSensor):
    """Tomorrow morning 2nd best price (highest) sensor."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tomorrow_morning_2nd_best_price",
            MORNING_BEST_WINDOW_START_HOUR,
            MORNING_BEST_WINDOW_END_HOUR,
            1,
        )


class RCETomorrowMorningBestPriceStartTimestampSensor(RCETomorrowBestWindowStartTimestampSensor):
    """Tomorrow morning best price start timestamp sensor."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tomorrow_morning_best_price_start_timestamp",
            MORNING_BEST_WINDOW_START_HOUR,
            MORNING_BEST_WINDOW_END_HOUR,
            0,
        )


class RCETomorrowMorningSecondBestPriceStartTimestampSensor(RCETomorrowBestWindowStartTimestampSensor):
    """Tomorrow morning 2nd best price start timestamp sensor."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tomorrow_morning_2nd_best_price_start_timestamp",
            MORNING_BEST_WINDOW_START_HOUR,
            MORNING_BEST_WINDOW_END_HOUR,
            1,
        )


class RCETomorrowEveningBestPriceSensor(RCETomorrowBestWindowPriceSensor):
    """Tomorrow evening best price (highest) sensor."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tomorrow_evening_best_price",
            EVENING_BEST_WINDOW_START_HOUR,
            EVENING_BEST_WINDOW_END_HOUR,
            0,
        )


class RCETomorrowEveningSecondBestPriceSensor(RCETomorrowBestWindowPriceSensor):
    """Tomorrow evening 2nd best price (highest) sensor."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tomorrow_evening_2nd_best_price",
            EVENING_BEST_WINDOW_START_HOUR,
            EVENING_BEST_WINDOW_END_HOUR,
            1,
        )


class RCETomorrowEveningBestPriceStartTimestampSensor(RCETomorrowBestWindowStartTimestampSensor):
    """Tomorrow evening best price start timestamp sensor."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tomorrow_evening_best_price_start_timestamp",
            EVENING_BEST_WINDOW_START_HOUR,
            EVENING_BEST_WINDOW_END_HOUR,
            0,
        )


class RCETomorrowEveningSecondBestPriceStartTimestampSensor(RCETomorrowBestWindowStartTimestampSensor):
    """Tomorrow evening 2nd best price start timestamp sensor."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            "tomorrow_evening_2nd_best_price_start_timestamp",
            EVENING_BEST_WINDOW_START_HOUR,
            EVENING_BEST_WINDOW_END_HOUR,
            1,
        )
