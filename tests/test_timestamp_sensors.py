from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.util import dt as dt_util

from custom_components.rce_prices.sensors.today_hours import (
    RCETodayMaxPriceHourStartTimestampSensor,
    RCETodayMaxPriceHourEndTimestampSensor,
    RCETodayMinPriceHourStartTimestampSensor,
    RCETodayMinPriceHourEndTimestampSensor,
)
from custom_components.rce_prices.sensors.tomorrow_hours import (
    RCETomorrowMaxPriceHourStartTimestampSensor,
    RCETomorrowMaxPriceHourEndTimestampSensor,
    RCETomorrowMinPriceHourStartTimestampSensor,
    RCETomorrowMinPriceHourEndTimestampSensor,
)
from custom_components.rce_prices.sensors.today_best_windows import (
    RCETodayMorningBestPriceStartTimestampSensor,
    RCETodayEveningSecondBestPriceStartTimestampSensor,
)


@pytest.fixture
def extended_api_data():
    now = dt_util.now()
    today = now.strftime("%Y-%m-%d")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    
    today_data = []
    tomorrow_data = []
    
    for hour in range(24):
        base_price = 300.0 + (hour * 5)
        if hour == 13:
            hourly_price = 200.0
        elif hour == 20:
            hourly_price = 550.0
        else:
            hourly_price = base_price
            
        for quarter in range(4):
            minutes = quarter * 15
            time_str = f"{hour:02d}:{minutes:02d}:00"
            dtime = f"{today} {time_str}"
            end_minutes = (quarter + 1) * 15
            if end_minutes == 60:
                end_hour = (hour + 1) % 24
                end_minutes = 0
            else:
                end_hour = hour
            end_time_str = f"{end_hour:02d}:{end_minutes:02d}"
            period = f"{hour:02d}:{minutes:02d} - {end_time_str}"
            
            today_data.append({
                "dtime": dtime,
                "period": period,
                "rce_pln": f"{hourly_price:.2f}",
                "business_date": today,
                "publication_ts": f"{today}T23:00:00Z"
            })
            
            tomorrow_base_price = 280.0 + (hour * 6)
            if hour == 14:
                tomorrow_hourly_price = 180.0
            elif hour == 19:
                tomorrow_hourly_price = 580.0
            else:
                tomorrow_hourly_price = tomorrow_base_price
            
            tomorrow_dtime = f"{tomorrow} {time_str}"
            tomorrow_data.append({
                "dtime": tomorrow_dtime,
                "period": period,
                "rce_pln": f"{tomorrow_hourly_price:.2f}",
                "business_date": tomorrow,
                "publication_ts": f"{today}T23:00:00Z"
            })
    
    return {
        "raw_data": today_data + tomorrow_data,
        "last_update": dt_util.now().isoformat(),
    }


@pytest.fixture
def mock_coordinator_extended(mock_hass, extended_api_data):
    coordinator = Mock()
    coordinator.hass = mock_hass
    coordinator.data = extended_api_data
    coordinator.last_update_success = True
    coordinator.last_update_success_time = dt_util.now()
    coordinator.async_add_listener = Mock()
    coordinator.async_remove_listener = Mock()
    return coordinator


class TestTodayMaxPriceTimestampSensors:

    def test_today_max_price_hour_start_timestamp_sensor_initialization(self, mock_coordinator):
        sensor = RCETodayMaxPriceHourStartTimestampSensor(mock_coordinator)
        
        assert sensor._attr_unique_id == "rce_prices_today_max_price_hour_start_timestamp"
        assert sensor._attr_device_class == SensorDeviceClass.TIMESTAMP
        assert sensor._attr_icon == "mdi:clock-start"

    def test_today_max_price_hour_start_timestamp_with_data(self, mock_coordinator_extended):
        sensor = RCETodayMaxPriceHourStartTimestampSensor(mock_coordinator_extended)
        
        timestamp = sensor.native_value
        
        assert timestamp is not None
        assert isinstance(timestamp, datetime)
        assert timestamp.hour == 20
        assert timestamp.minute == 0

    def test_today_max_price_hour_start_timestamp_no_data(self, mock_coordinator):
        sensor = RCETodayMaxPriceHourStartTimestampSensor(mock_coordinator)
        
        with patch.object(sensor, "get_today_data") as mock_today_data:
            mock_today_data.return_value = []
            
            timestamp = sensor.native_value
            assert timestamp is None

    def test_today_max_price_hour_end_timestamp_sensor_initialization(self, mock_coordinator):
        sensor = RCETodayMaxPriceHourEndTimestampSensor(mock_coordinator)
        
        assert sensor._attr_unique_id == "rce_prices_today_max_price_hour_end_timestamp"
        assert sensor._attr_device_class == SensorDeviceClass.TIMESTAMP
        assert sensor._attr_icon == "mdi:clock-end"

    def test_today_max_price_hour_end_timestamp_with_data(self, mock_coordinator_extended):
        sensor = RCETodayMaxPriceHourEndTimestampSensor(mock_coordinator_extended)
        
        timestamp = sensor.native_value
        
        assert timestamp is not None
        assert isinstance(timestamp, datetime)
        assert timestamp.hour == 21
        assert timestamp.minute == 0

    def test_today_max_price_hour_end_timestamp_no_data(self, mock_coordinator):
        sensor = RCETodayMaxPriceHourEndTimestampSensor(mock_coordinator)
        
        with patch.object(sensor, "get_today_data") as mock_today_data:
            mock_today_data.return_value = []
            
            timestamp = sensor.native_value
            assert timestamp is None

    def test_today_max_price_hour_timestamp_invalid_datetime(self, mock_coordinator):
        sensor = RCETodayMaxPriceHourStartTimestampSensor(mock_coordinator)
        
        with patch.object(sensor, "get_today_data") as mock_today_data:
            mock_today_data.return_value = [
                {"dtime": "invalid-datetime", "rce_pln": "500.00"}
            ]
            
            with patch.object(sensor.calculator, "find_extreme_price_records") as mock_find:
                mock_find.return_value = [{"dtime": "invalid-datetime", "rce_pln": "500.00"}]
                
                timestamp = sensor.native_value
                assert timestamp is None


class TestTodayMinPriceTimestampSensors:

    def test_today_min_price_hour_start_timestamp_sensor_initialization(self, mock_coordinator):
        sensor = RCETodayMinPriceHourStartTimestampSensor(mock_coordinator)
        
        assert sensor._attr_unique_id == "rce_prices_today_min_price_hour_start_timestamp"
        assert sensor._attr_device_class == SensorDeviceClass.TIMESTAMP
        assert sensor._attr_icon == "mdi:clock-start"

    def test_today_min_price_hour_start_timestamp_with_data(self, mock_coordinator_extended):
        sensor = RCETodayMinPriceHourStartTimestampSensor(mock_coordinator_extended)
        
        timestamp = sensor.native_value
        
        assert timestamp is not None
        assert isinstance(timestamp, datetime)
        assert timestamp.hour == 13
        assert timestamp.minute == 0

    def test_today_min_price_hour_start_timestamp_no_data(self, mock_coordinator):
        sensor = RCETodayMinPriceHourStartTimestampSensor(mock_coordinator)
        
        with patch.object(sensor, "get_today_data") as mock_today_data:
            mock_today_data.return_value = []
            
            timestamp = sensor.native_value
            assert timestamp is None

    def test_today_min_price_hour_end_timestamp_sensor_initialization(self, mock_coordinator):
        sensor = RCETodayMinPriceHourEndTimestampSensor(mock_coordinator)
        
        assert sensor._attr_unique_id == "rce_prices_today_min_price_hour_end_timestamp"
        assert sensor._attr_device_class == SensorDeviceClass.TIMESTAMP
        assert sensor._attr_icon == "mdi:clock-end"

    def test_today_min_price_hour_end_timestamp_with_data(self, mock_coordinator_extended):
        sensor = RCETodayMinPriceHourEndTimestampSensor(mock_coordinator_extended)
        
        timestamp = sensor.native_value
        
        assert timestamp is not None
        assert isinstance(timestamp, datetime)
        assert timestamp.hour == 14
        assert timestamp.minute == 0

    def test_today_min_price_hour_end_timestamp_no_data(self, mock_coordinator):
        sensor = RCETodayMinPriceHourEndTimestampSensor(mock_coordinator)
        
        with patch.object(sensor, "get_today_data") as mock_today_data:
            mock_today_data.return_value = []
            
            timestamp = sensor.native_value
            assert timestamp is None


class TestTodayBestWindowTimestampSensors:

    def test_today_morning_best_timestamp_sensor_initialization(self, mock_coordinator):
        sensor = RCETodayMorningBestPriceStartTimestampSensor(mock_coordinator)

        assert sensor._attr_unique_id == "rce_prices_today_morning_best_price_start_timestamp"
        assert sensor._attr_device_class == SensorDeviceClass.TIMESTAMP
        assert sensor._attr_icon == "mdi:clock-start"

    def test_today_evening_second_best_timestamp_sensor_initialization(self, mock_coordinator):
        sensor = RCETodayEveningSecondBestPriceStartTimestampSensor(mock_coordinator)

        assert sensor._attr_unique_id == "rce_prices_today_evening_2nd_best_price_start_timestamp"
        assert sensor._attr_device_class == SensorDeviceClass.TIMESTAMP
        assert sensor._attr_icon == "mdi:clock-start"

    def test_today_morning_best_timestamp_with_data(self, mock_coordinator):
        sensor = RCETodayMorningBestPriceStartTimestampSensor(mock_coordinator)

        with patch.object(sensor, "get_today_data") as mock_today_data:
            mock_today_data.return_value = [{"rce_pln": "100.00"}]

            with patch.object(sensor.calculator, "find_top_windows") as mock_find:
                mock_find.return_value = [
                    [
                        {"dtime": "2024-01-01 07:15:00", "rce_pln": "400.00"},
                        {"dtime": "2024-01-01 07:30:00", "rce_pln": "400.00"},
                        {"dtime": "2024-01-01 07:45:00", "rce_pln": "400.00"},
                        {"dtime": "2024-01-01 08:00:00", "rce_pln": "400.00"},
                    ],
                ]

                timestamp = sensor.native_value

                assert timestamp is not None
                assert isinstance(timestamp, datetime)
                assert timestamp.hour == 7
                assert timestamp.minute == 0

    def test_today_evening_second_best_timestamp_with_data(self, mock_coordinator):
        sensor = RCETodayEveningSecondBestPriceStartTimestampSensor(mock_coordinator)

        with patch.object(sensor, "get_today_data") as mock_today_data:
            mock_today_data.return_value = [{"rce_pln": "100.00"}]

            with patch.object(sensor.calculator, "find_top_windows") as mock_find:
                mock_find.return_value = [
                    [
                        {"dtime": "2024-01-01 17:15:00", "rce_pln": "500.00"},
                        {"dtime": "2024-01-01 17:30:00", "rce_pln": "500.00"},
                        {"dtime": "2024-01-01 17:45:00", "rce_pln": "500.00"},
                        {"dtime": "2024-01-01 18:00:00", "rce_pln": "500.00"},
                    ],
                    [
                        {"dtime": "2024-01-01 18:15:00", "rce_pln": "450.00"},
                        {"dtime": "2024-01-01 18:30:00", "rce_pln": "450.00"},
                        {"dtime": "2024-01-01 18:45:00", "rce_pln": "450.00"},
                        {"dtime": "2024-01-01 19:00:00", "rce_pln": "450.00"},
                    ],
                ]

                timestamp = sensor.native_value

                assert timestamp is not None
                assert isinstance(timestamp, datetime)
                assert timestamp.hour == 18
                assert timestamp.minute == 0


class TestTomorrowMaxPriceTimestampSensors:

    def test_tomorrow_max_price_hour_start_timestamp_sensor_initialization(self, mock_coordinator):
        sensor = RCETomorrowMaxPriceHourStartTimestampSensor(mock_coordinator)
        
        assert sensor._attr_unique_id == "rce_prices_tomorrow_max_price_hour_start_timestamp"
        assert sensor._attr_device_class == SensorDeviceClass.TIMESTAMP
        assert sensor._attr_icon == "mdi:clock-start"

    def test_tomorrow_max_price_hour_start_timestamp_availability(self, mock_coordinator):
        sensor = RCETomorrowMaxPriceHourStartTimestampSensor(mock_coordinator)
        
        with patch.object(sensor, "is_tomorrow_data_available") as mock_available:
            mock_available.return_value = False
            assert not sensor.available
            
            mock_available.return_value = True
            assert sensor.available

    def test_tomorrow_max_price_hour_start_timestamp_with_data(self, mock_coordinator_extended):
        sensor = RCETomorrowMaxPriceHourStartTimestampSensor(mock_coordinator_extended)
        
        with patch.object(sensor, "is_tomorrow_data_available") as mock_available:
            mock_available.return_value = True
            
            timestamp = sensor.native_value
            
            assert timestamp is not None
            assert isinstance(timestamp, datetime)
            assert timestamp.hour == 19
            assert timestamp.minute == 0

    def test_tomorrow_max_price_hour_start_timestamp_no_data(self, mock_coordinator):
        sensor = RCETomorrowMaxPriceHourStartTimestampSensor(mock_coordinator)
        
        with patch.object(sensor, "get_tomorrow_data") as mock_tomorrow_data:
            mock_tomorrow_data.return_value = []
            
            timestamp = sensor.native_value
            assert timestamp is None

    def test_tomorrow_max_price_hour_end_timestamp_sensor_initialization(self, mock_coordinator):
        sensor = RCETomorrowMaxPriceHourEndTimestampSensor(mock_coordinator)
        
        assert sensor._attr_unique_id == "rce_prices_tomorrow_max_price_hour_end_timestamp"
        assert sensor._attr_device_class == SensorDeviceClass.TIMESTAMP
        assert sensor._attr_icon == "mdi:clock-end"

    def test_tomorrow_max_price_hour_end_timestamp_with_data(self, mock_coordinator_extended):
        sensor = RCETomorrowMaxPriceHourEndTimestampSensor(mock_coordinator_extended)
        
        with patch.object(sensor, "is_tomorrow_data_available") as mock_available:
            mock_available.return_value = True
            
            timestamp = sensor.native_value
            
            assert timestamp is not None
            assert isinstance(timestamp, datetime)
            assert timestamp.hour == 20
            assert timestamp.minute == 0


class TestTomorrowMinPriceTimestampSensors:

    def test_tomorrow_min_price_hour_start_timestamp_sensor_initialization(self, mock_coordinator):
        sensor = RCETomorrowMinPriceHourStartTimestampSensor(mock_coordinator)
        
        assert sensor._attr_unique_id == "rce_prices_tomorrow_min_price_hour_start_timestamp"
        assert sensor._attr_device_class == SensorDeviceClass.TIMESTAMP
        assert sensor._attr_icon == "mdi:clock-start"

    def test_tomorrow_min_price_hour_start_timestamp_with_data(self, mock_coordinator_extended):
        sensor = RCETomorrowMinPriceHourStartTimestampSensor(mock_coordinator_extended)
        
        with patch.object(sensor, "is_tomorrow_data_available") as mock_available:
            mock_available.return_value = True
            
            timestamp = sensor.native_value
            
            assert timestamp is not None
            assert isinstance(timestamp, datetime)
            assert timestamp.hour == 14
            assert timestamp.minute == 0

    def test_tomorrow_min_price_hour_start_timestamp_no_data(self, mock_coordinator):
        sensor = RCETomorrowMinPriceHourStartTimestampSensor(mock_coordinator)
        
        with patch.object(sensor, "get_tomorrow_data") as mock_tomorrow_data:
            mock_tomorrow_data.return_value = []
            
            timestamp = sensor.native_value
            assert timestamp is None

    def test_tomorrow_min_price_hour_end_timestamp_sensor_initialization(self, mock_coordinator):
        sensor = RCETomorrowMinPriceHourEndTimestampSensor(mock_coordinator)
        
        assert sensor._attr_unique_id == "rce_prices_tomorrow_min_price_hour_end_timestamp"
        assert sensor._attr_device_class == SensorDeviceClass.TIMESTAMP
        assert sensor._attr_icon == "mdi:clock-end"

    def test_tomorrow_min_price_hour_end_timestamp_with_data(self, mock_coordinator_extended):
        sensor = RCETomorrowMinPriceHourEndTimestampSensor(mock_coordinator_extended)
        
        with patch.object(sensor, "is_tomorrow_data_available") as mock_available:
            mock_available.return_value = True
            
            timestamp = sensor.native_value
            
            assert timestamp is not None
            assert isinstance(timestamp, datetime)
            assert timestamp.hour == 15
            assert timestamp.minute == 0


class TestTimestampSensorErrorHandling:

    def test_extreme_price_sensors_missing_key_error(self, mock_coordinator):
        sensor = RCETodayMaxPriceHourStartTimestampSensor(mock_coordinator)
        
        with patch.object(sensor, "get_today_data") as mock_today_data:
            mock_today_data.return_value = [{"rce_pln": "500.00"}]
            
            with patch.object(sensor.calculator, "find_extreme_price_records") as mock_find:
                mock_find.return_value = [{"rce_pln": "500.00"}]
                
                timestamp = sensor.native_value
                assert timestamp is None

    def test_timestamp_sensors_empty_records_list(self, mock_coordinator):
        sensor = RCETodayMaxPriceHourStartTimestampSensor(mock_coordinator)
        
        with patch.object(sensor, "get_today_data") as mock_today_data:
            mock_today_data.return_value = [{"dtime": "2024-01-01 12:00:00", "rce_pln": "300.00"}]
            
            with patch.object(sensor.calculator, "find_extreme_price_records") as mock_find:
                mock_find.return_value = []
                
                timestamp = sensor.native_value
                assert timestamp is None 