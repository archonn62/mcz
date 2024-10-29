from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.mczmaestro.climate import MczClimateEntity
from homeassistant.components.climate import HVACMode


@pytest.fixture
def mock_controller():
    return MagicMock()


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    coordinator.data = {
        "Stove_State": 1,
        "Control_Mode": 0,
    }
    return coordinator


@pytest.fixture
def climate_entity(mock_controller, mock_coordinator):
    return MczClimateEntity(mock_controller, mock_coordinator, "Stove", "stove")


@pytest.mark.asyncio
async def test_async_set_hvac_mode_auto(climate_entity, mock_controller, mock_coordinator):
    mock_coordinator.data["Stove_State"] = 1
    await climate_entity.async_set_hvac_mode(HVACMode.AUTO)
    mock_controller.send.assert_any_call("C|WriteParametri|40|1")
    mock_coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_set_hvac_mode_heat(climate_entity, mock_controller, mock_coordinator):
    mock_coordinator.data["Stove_State"] = 1
    await climate_entity.async_set_hvac_mode(HVACMode.HEAT)
    mock_controller.send.assert_any_call("C|WriteParametri|40|0")
    mock_coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_set_hvac_mode_off(climate_entity, mock_controller, mock_coordinator):
    mock_coordinator.data["Stove_State"] = 1
    await climate_entity.async_set_hvac_mode(HVACMode.OFF)
    mock_controller.send.assert_any_call("C|WriteParametri|41|0")
    mock_controller.send.assert_any_call("C|WriteParametri|1111|0")
    mock_controller.send.assert_any_call("C|WriteParametri|34|40")
    mock_coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_set_hvac_mode_power_on(climate_entity, mock_controller, mock_coordinator):
    mock_coordinator.data["Stove_State"] = 0
    await climate_entity.async_set_hvac_mode(HVACMode.HEAT)
    mock_controller.send.assert_any_call("C|WriteParametri|34|1")
    mock_controller.send.assert_any_call("C|WriteParametri|40|0")
    mock_coordinator.async_request_refresh.assert_awaited_once()
