"""Time entities: start and end of each page's time window and of the quiet time.

They make the day plan changeable from a dashboard. Same start and end means "no limit".
"""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import schedule
from .const import A_SHOW_FROM, A_SHOW_UNTIL, CONF_QUIET_FROM, CONF_QUIET_UNTIL
from .coordinator import PixelClockConfigEntry
from .entity import PixelClockEntity


async def async_setup_entry(hass: HomeAssistant, entry: PixelClockConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities([
        QuietTime(coordinator, CONF_QUIET_FROM),
        QuietTime(coordinator, CONF_QUIET_UNTIL),
        *(
            AppWindowTime(coordinator, subentry, key)
            for subentry in coordinator.apps.values()
            for key in (A_SHOW_FROM, A_SHOW_UNTIL)
        ),
    ])


class _ScheduleTime(PixelClockEntity, TimeEntity):
    """A setting of Home Assistant, not of the panel: it can be changed while the panel is away."""

    _attr_entity_category = EntityCategory.CONFIG

    @property
    def available(self) -> bool:
        return True


class QuietTime(_ScheduleTime):
    def __init__(self, coordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._key = key

    @property
    def native_value(self) -> time | None:
        return schedule.parse_time(self.coordinator.options.get(self._key))

    async def async_set_value(self, value: time) -> None:
        entry = self.coordinator.config_entry
        self.hass.config_entries.async_update_entry(
            entry, options={**entry.options, self._key: schedule.format_time(value)}
        )


class AppWindowTime(_ScheduleTime):
    def __init__(self, coordinator, subentry: ConfigSubentry, key: str) -> None:
        super().__init__(coordinator, key)
        self._subentry_id = subentry.subentry_id
        self._key = key
        self._attr_unique_id = f"{coordinator.address}_{key}_{subentry.subentry_id}"
        self._attr_translation_placeholders = {"name": subentry.title}

    @property
    def _subentry(self) -> ConfigSubentry | None:
        return self.coordinator.config_entry.subentries.get(self._subentry_id)

    @property
    def native_value(self) -> time | None:
        return schedule.parse_time(self._subentry.data.get(self._key)) if self._subentry else None

    async def async_set_value(self, value: time) -> None:
        if (subentry := self._subentry) is not None:
            self.hass.config_entries.async_update_subentry(
                self.coordinator.config_entry, subentry,
                data={**subentry.data, self._key: schedule.format_time(value)},
            )
