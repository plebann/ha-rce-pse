from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_USE_HOURLY_PRICES,
    DEFAULT_USE_HOURLY_PRICES,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    vol.Optional(CONF_USE_HOURLY_PRICES, default=DEFAULT_USE_HOURLY_PRICES): selector.BooleanSelector(
        selector.BooleanSelectorConfig()
    ),
})


class RCEConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    MINOR_VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @staticmethod
    def async_get_options_flow(config_entry):
        return RCEOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        _LOGGER.debug("Starting RCE Prices config flow")
        
        if self._async_current_entries():
            _LOGGER.debug("RCE Prices integration already configured, aborting")
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            _LOGGER.debug("Creating RCE Prices config entry with options: %s", user_input)
            await self.async_set_unique_id("rce_prices")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="RCE Prices", data=user_input)

        _LOGGER.debug("Showing RCE Prices configuration form")
        return self.async_show_form(
            step_id="user", 
            data_schema=CONFIG_SCHEMA,
            errors={}
        )


class RCEOptionsFlow(config_entries.OptionsFlow):

    async def async_step_init(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            _LOGGER.debug("Updating RCE Prices options: %s", user_input)
            return self.async_create_entry(title="", data=user_input)

        current_data = self.config_entry.options if self.config_entry.options else self.config_entry.data
        options_schema = vol.Schema({
            vol.Optional(
                CONF_USE_HOURLY_PRICES, 
                default=current_data.get(CONF_USE_HOURLY_PRICES, DEFAULT_USE_HOURLY_PRICES)
            ): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors={}
        ) 