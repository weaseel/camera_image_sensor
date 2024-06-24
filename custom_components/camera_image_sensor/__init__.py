from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "camera_image_sensor"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True
