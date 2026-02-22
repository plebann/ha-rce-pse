from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final[str] = "rce_prices"
SENSOR_PREFIX: Final[str] = "RCE Prices"
MANUFACTURER: Final[str] = "plebann"
PSE_API_URL: Final[str] = "https://api.raporty.pse.pl/api/rce-pln"
API_UPDATE_INTERVAL: Final[timedelta] = timedelta(minutes=30)
API_SELECT: Final[str] = "dtime,period,rce_pln,business_date,publication_ts"
API_FIRST: Final[int] = 200

TAX_RATE: Final[float] = 0.23

CONF_USE_HOURLY_PRICES: Final[str] = "use_hourly_prices"

DEFAULT_USE_HOURLY_PRICES: Final[bool] = False 

MORNING_BEST_WINDOW_START_HOUR: Final[int] = 5
MORNING_BEST_WINDOW_END_HOUR: Final[int] = 10
EVENING_BEST_WINDOW_START_HOUR: Final[int] = 16
EVENING_BEST_WINDOW_END_HOUR: Final[int] = 22
BEST_WINDOW_DURATION_HOURS: Final[int] = 1

SERVICE_FIND_CHEAPEST_WINDOW: Final[str] = "find_cheapest_window"
ATTR_DURATION_HOURS: Final[str] = "duration_hours"
ATTR_START_HOUR: Final[str] = "start_hour"
ATTR_END_HOUR: Final[str] = "end_hour"

DEFAULT_SERVICE_START_HOUR: Final[int] = 8
DEFAULT_SERVICE_END_HOUR: Final[int] = 16
MIN_SERVICE_DURATION_HOURS: Final[int] = 1
MAX_SERVICE_DURATION_HOURS: Final[int] = 8