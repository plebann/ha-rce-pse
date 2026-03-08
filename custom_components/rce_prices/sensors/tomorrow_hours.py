from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.util import dt as dt_util

from .base import RCEBaseSensor
from ..const import CONF_MIN_PRICE_WINDOW_QUARTERS, DEFAULT_MIN_PRICE_WINDOW_QUARTERS

if TYPE_CHECKING:
    from ..coordinator import RCEPSEDataUpdateCoordinator


class RCETomorrowHoursSensor(RCEBaseSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator, unique_id: str) -> None:
        super().__init__(coordinator, unique_id)
        self._attr_icon = "mdi:clock"

    @property
    def available(self) -> bool:
        return super().available and self.is_tomorrow_data_available()

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

    def _get_min_price_window(self) -> list[dict]:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return []

        duration_quarters = self._get_min_price_window_duration_quarters()
        return self.calculator.find_cheapest_window(tomorrow_data, duration_quarters)

    def _get_window_boundaries(self, window: list[dict]) -> tuple[datetime, datetime] | None:
        if not window:
            return None

        try:
            first_dtime = datetime.strptime(window[0]["dtime"], "%Y-%m-%d %H:%M:%S")
            window_start = first_dtime - timedelta(minutes=15)

            last_dtime = datetime.strptime(window[-1]["dtime"], "%Y-%m-%d %H:%M:%S")
            window_end = last_dtime
        except (ValueError, KeyError, IndexError):
            return None

        return window_start, window_end


class RCETomorrowMaxPriceHourStartSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_max_price_hour_start")

    @property
    def native_value(self) -> str | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None
        
        max_price_records = self.calculator.find_extreme_price_records(tomorrow_data, is_max=True)
        return max_price_records[0]["period"].split(" - ")[0] if max_price_records else None


class RCETomorrowMaxPriceHourEndSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_max_price_hour_end")

    @property
    def native_value(self) -> str | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None
        
        max_price_records = self.calculator.find_extreme_price_records(tomorrow_data, is_max=True)
        return max_price_records[-1]["period"].split(" - ")[1] if max_price_records else None


class RCETomorrowMinPriceHourStartSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_min_price_hour_start")

    @property
    def native_value(self) -> str | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None
        
        min_price_records = self.calculator.find_extreme_price_records(tomorrow_data, is_max=False)
        return min_price_records[0]["period"].split(" - ")[0] if min_price_records else None


class RCETomorrowMinPriceHourEndSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_min_price_hour_end")

    @property
    def native_value(self) -> str | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None
        
        min_price_records = self.calculator.find_extreme_price_records(tomorrow_data, is_max=False)
        return min_price_records[-1]["period"].split(" - ")[1] if min_price_records else None


class RCETomorrowMaxPriceHourStartTimestampSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_max_price_hour_start_timestamp")
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-start"

    @property
    def native_value(self) -> datetime | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None
        
        max_price_records = self.calculator.find_extreme_price_records(tomorrow_data, is_max=True)
        if not max_price_records:
            return None
        
        try:
            start_time_str = max_price_records[0]["period"].split(" - ")[0]
            tomorrow_str = (dt_util.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            datetime_str = f"{tomorrow_str} {start_time_str}:00"
            start_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return dt_util.as_local(start_datetime)
        except (ValueError, KeyError, IndexError):
            return None


class RCETomorrowMaxPriceHourEndTimestampSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_max_price_hour_end_timestamp")
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-end"

    @property
    def native_value(self) -> datetime | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None
        
        max_price_records = self.calculator.find_extreme_price_records(tomorrow_data, is_max=True)
        if not max_price_records:
            return None
        
        try:
            end_time_str = max_price_records[-1]["period"].split(" - ")[1]
            tomorrow_str = (dt_util.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            datetime_str = f"{tomorrow_str} {end_time_str}:00"
            end_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return dt_util.as_local(end_datetime)
        except (ValueError, KeyError, IndexError):
            return None


class RCETomorrowMinPriceHourStartTimestampSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_min_price_hour_start_timestamp")
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-start"

    @property
    def native_value(self) -> datetime | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None
        
        min_price_records = self.calculator.find_extreme_price_records(tomorrow_data, is_max=False)
        if not min_price_records:
            return None
        
        try:
            start_time_str = min_price_records[0]["period"].split(" - ")[0]
            tomorrow_str = (dt_util.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            datetime_str = f"{tomorrow_str} {start_time_str}:00"
            start_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return dt_util.as_local(start_datetime)
        except (ValueError, KeyError, IndexError):
            return None


class RCETomorrowMinPriceHourEndTimestampSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_min_price_hour_end_timestamp")
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-end"

    @property
    def native_value(self) -> datetime | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None
        
        min_price_records = self.calculator.find_extreme_price_records(tomorrow_data, is_max=False)
        if not min_price_records:
            return None
        
        try:
            end_time_str = min_price_records[-1]["period"].split(" - ")[1]
            tomorrow_str = (dt_util.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            datetime_str = f"{tomorrow_str} {end_time_str}:00"
            end_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return dt_util.as_local(end_datetime)
        except (ValueError, KeyError, IndexError):
            return None


class RCETomorrowMaxPriceRangeSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_max_price_range")
        self._attr_icon = "mdi:clock-time-four"

    @property
    def native_value(self) -> str | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None
        
        max_price_records = self.calculator.find_extreme_price_records(tomorrow_data, is_max=True)
        if not max_price_records:
            return None
            
        start_time = max_price_records[0]["period"].split(" - ")[0]
        end_time = max_price_records[-1]["period"].split(" - ")[1]
        return f"{start_time} - {end_time}" 


class RCETomorrowMinPriceWindowAvgPriceSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_min_price_window_avg_price")
        self._attr_native_unit_of_measurement = "PLN/MWh"
        self._attr_icon = "mdi:cash"

    @property
    def native_value(self) -> float | None:
        window = self._get_min_price_window()
        if not window:
            return None

        try:
            window_prices = [float(record["rce_pln"]) for record in window]
            return round(sum(window_prices) / len(window_prices), 2)
        except (ValueError, KeyError):
            return None


class RCETomorrowMinPriceWindowStartTimestampSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_min_price_window_start_timestamp")
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-start"

    @property
    def native_value(self) -> datetime | None:
        window = self._get_min_price_window()
        boundaries = self._get_window_boundaries(window)
        if not boundaries:
            return None

        window_start, _ = boundaries
        return dt_util.as_local(window_start)


class RCETomorrowMinPriceWindowEndTimestampSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_min_price_window_end_timestamp")
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-end"

    @property
    def native_value(self) -> datetime | None:
        window = self._get_min_price_window()
        boundaries = self._get_window_boundaries(window)
        if not boundaries:
            return None

        _, window_end = boundaries
        return dt_util.as_local(window_end)


class RCETomorrowMinPriceWindowRangeSensor(RCETomorrowHoursSensor):

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "tomorrow_min_price_window_range")
        self._attr_icon = "mdi:clock-time-four"

    @property
    def native_value(self) -> str | None:
        window = self._get_min_price_window()
        boundaries = self._get_window_boundaries(window)
        if not boundaries:
            return None

        window_start, window_end = boundaries
        start_time = window_start.strftime("%H:%M")
        end_time = window_end.strftime("%H:%M")
        return f"{start_time} - {end_time}"