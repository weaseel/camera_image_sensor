import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
import logging

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class CameraImageSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        _LOGGER.debug("Starting async_step_user with user_input: %s", user_input)
        errors = {}
        if user_input is not None:
            try:
                _LOGGER.debug("Creating entry with user_input: %s", user_input)
                return self.async_create_entry(title="Camera Image Sensor", data=user_input)
            except Exception as e:
                _LOGGER.error("Error creating entry: %s", e)
                errors["base"] = "unknown"
        
        try:
            data_schema = vol.Schema({
                vol.Required("camera_entity"): cv.entity_domain('camera'),
                vol.Optional("scan_interval", default=60): cv.positive_int
            })
            return self.async_show_form(
                step_id="user",
                data_schema=data_schema,
                errors=errors
            )
        except Exception as e:
            _LOGGER.error("Error showing form: %s", e)
            return self.async_abort(reason="unknown_error")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        _LOGGER.debug("Getting options flow for config_entry: %s", config_entry)
        return CameraImageSensorOptionsFlowHandler(config_entry)

class CameraImageSensorOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        _LOGGER.debug("Starting async_step_init with user_input: %s", user_input)
        if user_input is not None:
            try:
                _LOGGER.debug("Creating entry with user_input: %s", user_input)
                return self.async_create_entry(title="", data=user_input)
            except Exception as e:
                _LOGGER.error("Error creating entry: %s", e)

        try:
            data_schema = vol.Schema({
                vol.Optional("scan_interval", default=self.config_entry.options.get("scan_interval", 60)): cv.positive_int
            })
            return self.async_show_form(
                step_id="init",
                data_schema=data_schema
            )
        except Exception as e:
            _LOGGER.error("Error showing form: %s", e)
            return self.async_abort(reason="unknown_error")
