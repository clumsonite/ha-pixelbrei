"""Time entities: when the panel switches on and off, so a dashboard can change it.

Same on and off time means the slot is not used.
"""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import schedule
from .const import SCHEDULE_SLOTS
from .coordinator import PixelClockConfigEntry
from .entity import PixelClockEntity


async def async_setup_entry(hass: HomeAssistant, entry: PixelClockConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities(ScheduleTime(coordinator, key) for slot in SCHEDULE_SLOTS for key in slot)


class ScheduleTime(PixelClockEntity, TimeEntity):
    """A setting of Home Assistant, not of the panel: it can be changed while the panel is away."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._key = key

    @property
    def available(self) -> bool:
        return True

    @property
    def native_value(self) -> time | None:
        return schedule.parse_time(self.coordinator.options.get(self._key))

    async def async_set_value(self, value: time) -> None:
        entry = self.coordinator.config_entry
        self.hass.config_entries.async_update_entry(
            entry, options={**entry.options, self._key: schedule.format_time(value)}
        )
