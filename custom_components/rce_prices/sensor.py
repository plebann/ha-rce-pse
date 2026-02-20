from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .sensors import (
    RCETodayMainSensor,
    RCETodayAvgPriceSensor,
    RCETodayMaxPriceSensor,
    RCETodayMinPriceSensor,
    RCETodayMaxPriceHourStartSensor,
    RCETodayMaxPriceHourEndSensor,
    RCETodayMinPriceHourStartSensor,
    RCETodayMinPriceHourEndSensor,
    RCETodayMaxPriceHourStartTimestampSensor,
    RCETodayMaxPriceHourEndTimestampSensor,
    RCETodayMinPriceHourStartTimestampSensor,
    RCETodayMinPriceHourEndTimestampSensor,
    RCETodayMinPriceRangeSensor,
    RCETodayMaxPriceRangeSensor,
    RCETodayMedianPriceSensor,
    RCETodayCurrentVsAverageSensor,
    RCETodayMorningBestPriceSensor,
    RCETodayMorningSecondBestPriceSensor,
    RCETodayMorningBestPriceStartTimestampSensor,
    RCETodayMorningSecondBestPriceStartTimestampSensor,
    RCETodayEveningBestPriceSensor,
    RCETodayEveningSecondBestPriceSensor,
    RCETodayEveningBestPriceStartTimestampSensor,
    RCETodayEveningSecondBestPriceStartTimestampSensor,
    RCETomorrowMainSensor,
    RCETomorrowAvgPriceSensor,
    RCETomorrowMaxPriceSensor,
    RCETomorrowMinPriceSensor,
    RCETomorrowMaxPriceHourStartSensor,
    RCETomorrowMaxPriceHourEndSensor,
    RCETomorrowMinPriceHourStartSensor,
    RCETomorrowMinPriceHourEndSensor,
    RCETomorrowMaxPriceHourStartTimestampSensor,
    RCETomorrowMaxPriceHourEndTimestampSensor,
    RCETomorrowMinPriceHourStartTimestampSensor,
    RCETomorrowMinPriceHourEndTimestampSensor,
    RCETomorrowMinPriceRangeSensor,
    RCETomorrowMaxPriceRangeSensor,
    RCETomorrowMedianPriceSensor,
    RCETomorrowTodayAvgComparisonSensor,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug("Setting up RCE Prices sensors for config entry: %s", config_entry.entry_id)
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    sensors = [
        RCETodayMainSensor(coordinator),
        RCETodayAvgPriceSensor(coordinator),
        RCETodayMaxPriceSensor(coordinator),
        RCETodayMinPriceSensor(coordinator),
        RCETodayMaxPriceHourStartSensor(coordinator),
        RCETodayMaxPriceHourEndSensor(coordinator),
        RCETodayMinPriceHourStartSensor(coordinator),
        RCETodayMinPriceHourEndSensor(coordinator),
        RCETodayMaxPriceHourStartTimestampSensor(coordinator),
        RCETodayMaxPriceHourEndTimestampSensor(coordinator),
        RCETodayMinPriceHourStartTimestampSensor(coordinator),
        RCETodayMinPriceHourEndTimestampSensor(coordinator),
        RCETodayMinPriceRangeSensor(coordinator),
        RCETodayMaxPriceRangeSensor(coordinator),
        RCETodayMedianPriceSensor(coordinator),
        RCETodayCurrentVsAverageSensor(coordinator),
        RCETodayMorningBestPriceSensor(coordinator),
        RCETodayMorningSecondBestPriceSensor(coordinator),
        RCETodayMorningBestPriceStartTimestampSensor(coordinator),
        RCETodayMorningSecondBestPriceStartTimestampSensor(coordinator),
        RCETodayEveningBestPriceSensor(coordinator),
        RCETodayEveningSecondBestPriceSensor(coordinator),
        RCETodayEveningBestPriceStartTimestampSensor(coordinator),
        RCETodayEveningSecondBestPriceStartTimestampSensor(coordinator),
        RCETomorrowMainSensor(coordinator),
        RCETomorrowAvgPriceSensor(coordinator),
        RCETomorrowMaxPriceSensor(coordinator),
        RCETomorrowMinPriceSensor(coordinator),
        RCETomorrowMaxPriceHourStartSensor(coordinator),
        RCETomorrowMaxPriceHourEndSensor(coordinator),
        RCETomorrowMinPriceHourStartSensor(coordinator),
        RCETomorrowMinPriceHourEndSensor(coordinator),
        RCETomorrowMaxPriceHourStartTimestampSensor(coordinator),
        RCETomorrowMaxPriceHourEndTimestampSensor(coordinator),
        RCETomorrowMinPriceHourStartTimestampSensor(coordinator),
        RCETomorrowMinPriceHourEndTimestampSensor(coordinator),
        RCETomorrowMinPriceRangeSensor(coordinator),
        RCETomorrowMaxPriceRangeSensor(coordinator),
        RCETomorrowMedianPriceSensor(coordinator),
        RCETomorrowTodayAvgComparisonSensor(coordinator),
    ]
    
    _LOGGER.debug("Adding %d RCE Prices sensors to Home Assistant", len(sensors))
    async_add_entities(sensors)
    _LOGGER.debug("RCE Prices sensors setup completed successfully") 