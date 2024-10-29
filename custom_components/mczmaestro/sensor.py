"""Support for the MCZ sensors."""

import logging
from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONTROLLER, COORDINATOR, DOMAIN
from .entity import MczEntity
from .lib.controller import MaestroController, get_maestro_state_description

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MCZ platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    controller = data[CONTROLLER]
    coordinator = data[COORDINATOR]

    entities = [
        MczStateEntity(controller, coordinator, name="State", command_name="state"),
        MczSensorEntity(
            controller,
            coordinator,
            "Temperature",
            "Ambient_Temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
        ),
    ]

    if entities:
        async_add_entities(entities)


class MczStateEntity(MczEntity, SensorEntity):
    """Representation of a debug sensor."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str:
        """Return the state."""
        _LOGGER.debug("State entity debug")
        _LOGGER.debug(self.coordinator.data)
        if "Stove_State" in self.coordinator.data:
            return get_maestro_state_description(
                int(self.coordinator.data["Stove_State"])
            )
        return "unknown"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data:
            return self.coordinator.data
        return {}


class MczSensorEntity(MczEntity, SensorEntity):
    """Representation of a MCZ sensor."""

    def __init__(  # noqa: PLR0913
        self,
        controller: MaestroController,
        coordinator,
        name,
        command_name,
        device_class: SensorDeviceClass,
        unit_of_measurement: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(controller, coordinator, name, command_name)
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement

    @property
    def native_value(self) -> float:
        """Return the state."""
        return self.coordinator.data[self._command_name]
