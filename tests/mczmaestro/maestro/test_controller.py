from unittest.mock import MagicMock, patch

from custom_components.mczmaestro.maestro.controller import MaestroController

TEST_HOST = "192.168.121.1"
TEST_PORT = 81
TEST_TIMEOUT = 60


@patch("custom_components.mczmaestro.maestro.websocket.create_connection")
def test_init_success(mock_create_connection):
    # Arrange
    mock_ws = MagicMock()
    mock_create_connection.return_value = mock_ws

    # Act
    controller = MaestroController(TEST_HOST, TEST_PORT)

    # Assert
    assert controller.host == TEST_HOST
    assert controller.port == TEST_PORT
    mock_create_connection.assert_called_once_with(f"ws://{TEST_HOST}:{TEST_PORT}", timeout=TEST_TIMEOUT)
    assert controller._server == mock_ws  # noqa: SLF001


@patch("custom_components.mczmaestro.maestro.websocket.create_connection")
def test_init_default_timeout(mock_create_connection):
    # Arrange
    mock_ws = MagicMock()
    mock_create_connection.return_value = mock_ws

    # Act
    controller = MaestroController(TEST_HOST, TEST_PORT)

    # Assert
    assert controller.host == TEST_HOST
    assert controller.port == TEST_PORT
    mock_create_connection.assert_called_once_with(f"ws://{TEST_HOST}:{TEST_PORT!s}", timeout=60)
    assert controller._server == mock_ws  # noqa: SLF001


@patch("custom_components.mczmaestro.maestro.websocket.create_connection")
def test_receive_message(mock_create_connection):
    # Arrange
    mock_ws = MagicMock()
    mock_create_connection.return_value = mock_ws

    controller = MaestroController(TEST_HOST, TEST_PORT)
    controller._server = MagicMock()  # noqa: SLF001
    controller._server.recv.return_value = "01|00|06|06|00|0016|2c|ff|00|ff|00|0094|0000|0000|0000|00|00|ff|00|29|01|0063|01|01|01|01|28|46|39|0d|010b01|04|00|28|1a|0a|07e8|007a1f56|001c78ca|0002abf8|0002d7ef|00042266|000ffeba|0720|0000|09dd|003c|00|00|00|00|00|ff|ff|ff|ff|40|32|ff|ff|01|00"  # noqa: SLF001 E501

    expected_output = {
        "Messagetype": "1",
        "Stove_State": "0",
        "Power": "False",
        "Diagnostics": "False",
        "Fan_State": "6",
        "DuctedFan1": "6",
        "DuctedFan2": "0",
        "Fume_Temperature": "22",
        "Ambient_Temperature": "22.0",
        "Puffer_Temperature": "127.5",
        "Boiler_Temperature": "0.0",
        "NTC3_Temperature": "127.5",
        "Candle_Condition": "0",
        "ACTIVE_Set": "148",
        "RPM_Fam_Fume": "0",
        "RPM_WormWheel_Set": "0",
        "RPM_WormWheel_Live": "0",
        "3WayValve": "Risc",
        "Pump_PWM": "0",
        "Brazier": "CLR",
        "Profile": "0",
        "Modbus_Address": "41",
        "Active_Mode": "1",
        "Active_Live": "99",
        "Control_Mode": "1",
        "Eco_Mode": "1",
        "Silent_Mode": "1",
        "Chronostat": "1",
        "Temperature_Setpoint": "20.0",
        "Boiler_Setpoint": "35.0",
        "Temperature_Motherboard": "28.5",
        "Power_Level": "13",
        "FirmwareVersion": "68353",
        "DatabaseID": "4",
        "Date_Time_Hours": "0",
        "Date_Time_Minutes": "40",
        "Date_Day_Of_Month": "26",
        "Date_Month": "10",
        "Date_Year": "2024",
        "Total_Operating_Hours": "2223:10:14",
        "Hours_Of_Operation_In_Power1": "518:18:50",
        "Hours_Of_Operation_In_Power2": "48:38:16",
        "Hours_Of_Operation_In_Power3": "51:45:51",
        "Hours_Of_Operation_In_Power4": "75:15:50",
        "Hours_Of_Operation_In_Power5": "291:10:50",
        "Hours_To_Service": "1824",
        "Minutes_To_Switch_Off": "0",
        "Number_Of_Ignitions": "2525",
        "Active_Temperature": "60",
        "Celcius_Or_Fahrenheit": "0",
        "Sound_Effects": "0",
        "Sound_Effects_State": "0",
        "Sleep": "0",
        "Mode": "0",
        "WifiSondeTemperature1": "255",
        "WifiSondeTemperature2": "255",
        "WifiSondeTemperature3": "255",
        "Unknown": "255",
        "SetPuffer": "64",
        "SetBoiler": "50",
        "SetHealth": "255",
        "Return_Temperature": "127.5",
        "AntiFreeze": "1",
        "SetPuffer2": "0",
    }

    # Act
    result = controller.receive()

    # Assert
    assert result == expected_output
