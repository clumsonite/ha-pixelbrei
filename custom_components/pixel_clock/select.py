"""Select entities: display mode, orientation, page transition and the panel's built-in clock face."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import protocol as proto
from . import render, transitions
from .const import MODES
from .coordinator import PixelClockConfigEntry
from .entity import PixelClockEntity


async def async_setup_entry(hass: HomeAssistant, entry: PixelClockConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities([
        ModeSelect(coordinator, "mode"),
        ClockStyleSelect(coordinator, "clock_style"),
        OrientationSelect(coordinator, "orientation"),
        TransitionSelect(coordinator, "transition"),
    ])


class ModeSelect(PixelClockEntity, SelectEntity):
    _attr_options = list(MODES)

    @property
    def current_option(self) -> str:
        return self.coordinator.settings.mode

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_settings(mode=option)


class TransitionSelect(PixelClockEntity, SelectEntity):
    """How the rotation moves from one page to the next."""

    _attr_options = list(transitions.TRANSITIONS)

    @property
    def current_option(self) -> str:
        current = self.coordinator.settings.transition
        return current if current in transitions.TRANSITIONS else transitions.NONE

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_settings(transition=option)


class OrientationSelect(PixelClockEntity, SelectEntity):
    """Landscape, portrait (panel turned left or right) or upside down; Home Assistant rotates the picture."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(render.ORIENTATIONS)

    @property
    def current_option(self) -> str:
        return self.coordinator.settings.orientation

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_settings(orientation=option)


class ClockStyleSelect(PixelClockEntity, SelectEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = [str(i) for i in range(proto.CLOCK_STYLES)]

    @property
    def current_option(self) -> str:
        return str(self.coordinator.settings.clock_style)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_settings(clock_style=int(option))

