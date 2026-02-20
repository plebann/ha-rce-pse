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

MORNING_BEST_WINDOW_START_HOUR: Final[int] = 7
MORNING_BEST_WINDOW_END_HOUR: Final[int] = 9
EVENING_BEST_WINDOW_START_HOUR: Final[int] = 17
EVENING_BEST_WINDOW_END_HOUR: Final[int] = 21
BEST_WINDOW_DURATION_HOURS: Final[int] = 1