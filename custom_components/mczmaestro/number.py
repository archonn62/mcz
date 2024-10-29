"""Support for MCZ numbers."""

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONTROLLER, COORDINATOR, DOMAIN
from .entity import MczEntity
from .maestro.controller import MaestroController

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IPX800 switches."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    controller = data[CONTROLLER]
    coordinator = data[COORDINATOR]

    entities = [
        MczNumberEntity(controller, coordinator, "Temperature T1", "Chronostat_T1", 1108),
        MczNumberEntity(controller, coordinator, "Temperature T2", "Chronostat_T2", 1109),
        MczNumberEntity(controller, coordinator, "Temperature T3", "Chronostat_T3", 1110),
    ]

    async_add_entities(entities, True)


class MczNumberEntity(MczEntity, NumberEntity):
    """Representation a Mcz number."""

    _attr_native_max_value = 30
    _attr_native_min_value = 8
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        controller: MaestroController,
        coordinator: DataUpdateCoordinator,
        name: str,
        command_name: str,
        command_id: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(controller, coordinator, name, command_name)
        self._command_id: int = command_id
        self._value: float = 0

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self.coordinator.data.get(self._command_name, self._value)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.controller.send(f"C|WriteParametri|{self._command_id!s}|{value!s}")
        # set value in local if it's not return by the strove
        self._value = value
        await self.coordinator.async_request_refresh()
