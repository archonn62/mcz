from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mczmaestro.config_flow import MczConfigFlow
from custom_components.mczmaestro.const import DOMAIN
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.data_entry_flow import FlowResultType

"""Test the mczmaestro config flow."""


TEST_USER_INPUT = {
    CONF_HOST: "192.168.120.1",
    CONF_PORT: 81,
    CONF_SCAN_INTERVAL: 30,
}


@pytest.fixture
def mock_maestro_controller():
    with patch("custom_components.mczmaestro.config_flow.MaestroController") as mock:
        mock.return_value.host = "192.168.120.1"
        mock.return_value.port = 81
        mock.return_value.connected = True
        yield mock


@pytest.mark.asyncio
async def test_show_form(hass):
    """Test that the form is served with no input."""
    # Create a mock config entry
    mock_entry = MockConfigEntry(
        domain="mczmaestro",
        data=TEST_USER_INPUT,
    )
    # Add the mock entry to hass
    mock_entry.add_to_hass(hass)

    flow = MczConfigFlow()
    flow.hass = hass

    result = await flow.async_step_user(user_input=None)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_create_entry(hass, mock_maestro_controller):
    """Test that the config entry is created."""

    flow = MczConfigFlow()
    flow.hass = hass

    with (
        patch.object(flow, "async_set_unique_id", return_value=None),
        patch.object(flow, "_abort_if_unique_id_configured"),
    ):
        result = await flow.async_step_user(user_input=TEST_USER_INPUT)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "MCZ Maestro 192.168.120.1:81"
    assert result["data"] == TEST_USER_INPUT


@pytest.mark.asyncio
async def test_abort_if_unique_id_configured(hass, mock_maestro_controller):
    """Test that the flow aborts if the unique ID is already configured."""
    # Create a mock config entry with the same unique ID
    mock_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="_".join([DOMAIN, TEST_USER_INPUT[CONF_HOST], str(TEST_USER_INPUT[CONF_PORT])]),
        data=TEST_USER_INPUT,
    )
    mock_entry.add_to_hass(hass)

    flow = MczConfigFlow()
    flow.hass = hass

    with (
        patch.object(flow, "async_set_unique_id", return_value=True),
        patch.object(flow, "_abort_if_unique_id_configured") as mock_abort,
    ):
        await flow.async_step_user(user_input=TEST_USER_INPUT)

    mock_abort.assert_called_once()


@pytest.mark.asyncio
async def test_show_form_on_connection_error(hass, mock_maestro_controller):
    """Test that the form is re-displayed on connection error."""
    mock_maestro_controller.return_value.connected = False

    flow = MczConfigFlow()
    flow.hass = hass

    with (
        patch.object(flow, "async_set_unique_id", return_value=None),
        patch.object(flow, "_abort_if_unique_id_configured"),
    ):
        result = await flow.async_step_user(user_input=TEST_USER_INPUT)

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
