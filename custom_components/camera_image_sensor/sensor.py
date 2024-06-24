import logging
from datetime import timedelta
from PIL import Image
from io import BytesIO

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.helpers.entity_component import EntityComponent

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    camera_entity = entry.data["camera_entity"]
    scan_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    
    coordinator = ImageAnalysisCoordinator(hass, camera_entity, scan_interval)
    await coordinator.async_refresh()

    sensor = CameraImageSensor(coordinator, camera_entity)
    async_add_entities([sensor], True)

    # Add a service to trigger the analysis manually
    platform = EntityComponent(_LOGGER, "sensor", hass)
    platform.async_register_entity_service(
        "trigger_analysis",
        {},
        "async_trigger_analysis",
    )

    async def handle_trigger_service(call):
        await sensor.async_trigger_analysis()

    hass.services.async_register(DOMAIN, "trigger_analysis", handle_trigger_service)

class ImageAnalysisCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, camera_entity, scan_interval):
        self.camera_entity = camera_entity
        self.scan_interval = scan_interval if scan_interval > timedelta(0) else None
        super().__init__(hass, _LOGGER, name="Camera Image Sensor", update_interval=self.scan_interval)

    async def _async_update_data(self):
        try:
            image = await self.hass.components.camera.async_get_image(self.camera_entity)
            return self._is_bw(Image.open(BytesIO(image.content)))
        except Exception as e:
            _LOGGER.error("Error fetching image: %s", e)
            return None

    def _is_bw(self, image):
        grayscale = image.convert("L")
        rgb = grayscale.convert("RGB")
        return "bw" if list(image.getdata()) == list(rgb.getdata()) else "color"

class CameraImageSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, camera_entity):
        super().__init__(coordinator)
        self._camera_entity = camera_entity
        self._attr_name = "Camera Image Sensor"
        self._attr_unique_id = f"camera_image_sensor_{camera_entity}"

    @property
    def state(self):
        return self.coordinator.data

    async def async_trigger_analysis(self):
        await self.coordinator.async_request_refresh()
