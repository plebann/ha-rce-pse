from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .binary_sensors import (
    RCETodayMinPriceWindowBinarySensor,
    RCETodayMaxPriceWindowBinarySensor,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug("Setting up RCE Prices binary sensors for config entry: %s", config_entry.entry_id)
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    binary_sensors = [
        RCETodayMinPriceWindowBinarySensor(coordinator),
        RCETodayMaxPriceWindowBinarySensor(coordinator),
    ]
    
    _LOGGER.debug("Adding %d RCE Prices binary sensors to Home Assistant", len(binary_sensors))
    async_add_entities(binary_sensors)
    _LOGGER.debug("RCE Prices binary sensors setup completed successfully") 