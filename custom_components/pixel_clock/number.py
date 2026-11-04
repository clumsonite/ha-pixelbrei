"""Number entities: brightness of the panel, how long each app is shown."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import MAX_APP_SECONDS, MIN_APP_SECONDS
from .coordinator import PixelClockConfigEntry
from .entity import PixelClockEntity


async def async_setup_entry(hass: HomeAssistant, entry: PixelClockConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities([BrightnessNumber(coordinator, "brightness"), AppDurationNumber(coordinator, "app_duration")])


class BrightnessNumber(PixelClockEntity, NumberEntity):
    """Brightness as a plain slider on the device page (the light entity hides it in its dialog)."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 1
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self) -> int:
        return self.coordinator.settings.brightness

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_brightness(int(value))


class AppDurationNumber(PixelClockEntity, NumberEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = MIN_APP_SECONDS
    _attr_native_max_value = MAX_APP_SECONDS
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    @property
    def native_value(self) -> int:
        return self.coordinator.settings.app_seconds

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_settings(app_seconds=int(value))
