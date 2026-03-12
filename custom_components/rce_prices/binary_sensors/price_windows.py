from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from .base import RCEBaseBinarySensor
from ..const import CONF_MIN_PRICE_WINDOW_QUARTERS, DEFAULT_MIN_PRICE_WINDOW_QUARTERS

if TYPE_CHECKING:
    from ..coordinator import RCEPSEDataUpdateCoordinator


class RCETodayMaxPriceWindowBinarySensor(RCEBaseBinarySensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "today_max_price_window_active")
        self._attr_icon = "mdi:clock-alert"

    @property
    def is_on(self) -> bool:
        today_data = self.get_today_data()
        if not today_data:
            return False
        
        max_price_records = self.calculator.find_extreme_price_records(today_data, is_max=True)
        if not max_price_records:
            return False
        
        start_time = max_price_records[0]["period"].split(" - ")[0]
        end_time = max_price_records[-1]["period"].split(" - ")[1]
        
        return self.is_current_time_in_window(start_time, end_time)


class RCETodayMinPriceWindowBinarySensor(RCEBaseBinarySensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "today_min_price_window_active")
        self._attr_icon = "mdi:clock-check"

    def _get_min_price_window_duration_quarters(self) -> int:
        duration = self.coordinator._get_config_value(
            CONF_MIN_PRICE_WINDOW_QUARTERS,
            DEFAULT_MIN_PRICE_WINDOW_QUARTERS,
        )
        try:
            parsed_duration = int(float(duration))
        except (TypeError, ValueError):
            return DEFAULT_MIN_PRICE_WINDOW_QUARTERS

        return parsed_duration if parsed_duration > 0 else DEFAULT_MIN_PRICE_WINDOW_QUARTERS

    @property
    def is_on(self) -> bool:
        today_data = self.get_today_data()
        if not today_data:
            return False

        duration_quarters = self._get_min_price_window_duration_quarters()
        min_price_window = self.calculator.find_cheapest_window(today_data, duration_quarters)
        if not min_price_window:
            return False

        try:
            first_dtime = datetime.strptime(min_price_window[0]["dtime"], "%Y-%m-%d %H:%M:%S")
            window_start = first_dtime - timedelta(minutes=15)

            last_dtime = datetime.strptime(min_price_window[-1]["dtime"], "%Y-%m-%d %H:%M:%S")
            window_end = last_dtime
        except (ValueError, KeyError, IndexError):
            return False

        return self.is_current_time_in_window(
            window_start.strftime("%H:%M"),
            window_end.strftime("%H:%M"),
            window_start.strftime("%Y-%m-%d"),
        )