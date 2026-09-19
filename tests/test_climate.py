"""Compatibility checks against the installed Home Assistant version."""
from unittest.mock import patch

import pytest
from homeassistant.components.climate import HVACMode, HVACAction
from homeassistant.const import UnitOfTemperature
from homeassistant.setup import async_setup_component

from custom_components.infinitive.climate import InfinitiveDevice, PLATFORM_SCHEMA


@pytest.fixture
def entity(device):
    return InfinitiveDevice(device, "Infinitive", 2, UnitOfTemperature.FAHRENHEIT, "test:8080")


def test_yaml_configuration():
    config = PLATFORM_SCHEMA({"platform": "infinitive", "host": "192.0.2.1"})
    assert config["port"] == 8080
    assert config["tempunits"] == "fahrenheit"


@pytest.mark.parametrize("device_mode,ha_mode", [
    ("heat", HVACMode.HEAT), ("cool", HVACMode.COOL),
    ("auto", HVACMode.HEAT_COOL), ("off", HVACMode.OFF),
])
def test_mode_mapping(entity, device, device_mode, ha_mode):
    device.status["mode"] = device_mode
    entity.update()
    assert entity.hvac_mode == ha_mode
    entity.set_hvac_mode(ha_mode)
    device.set_mode.assert_called_once_with(device_mode)


def test_readings(entity):
    assert entity.current_temperature == 70
    assert entity.target_temperature == 68
    assert entity.hvac_action == HVACAction.HEATING
    assert entity.extra_state_attributes["current_humidity"] == 42


@pytest.mark.parametrize("mode,temperature,target", [("heat", 69, "heat"), ("cool", 76, "cool")])
def test_single_setpoint(entity, device, mode, temperature, target):
    device.status["mode"] = mode
    entity.update()
    entity.set_temperature(temperature=temperature)
    device.set_temp.assert_called_once_with(temperature, target)


def test_range_setpoint(entity, device):
    device.status["mode"] = "auto"
    entity.update()
    entity.set_temperature(target_temp_low=70, target_temp_high=71)
    assert [call.args for call in device.set_temp.call_args_list] == [(71, "cool"), (69, "heat")]


@pytest.mark.parametrize("ha_fan,device_fan", [("auto", "auto"), ("low", "low"), ("medium", "med"), ("high", "high")])
def test_fan_control(entity, device, ha_fan, device_fan):
    entity.set_fan_mode(ha_fan)
    device.set_fanmode.assert_called_once_with(device_fan)


@pytest.mark.parametrize("preset,hold", [("Hold", True), ("home", False)])
def test_hold_control(entity, device, preset, hold):
    entity.set_preset_mode(preset)
    device.set_hold.assert_called_once_with(hold)


def test_reading_recovers_after_connection_error(entity, device):
    # Current behavior propagates transport errors to HA's polling machinery.
    device.get_status.side_effect = ConnectionError("Simulated outage")
    with pytest.raises(ConnectionError):
        entity.update()
    device.status["currentTemp"] = 72
    device.get_status.side_effect = lambda: dict(device.status)
    entity.update()
    assert entity.current_temperature == 72


async def test_load_and_services(hass, device):
    """Load YAML through HA and exercise its actual service dispatch."""
    with patch("pyinfinitive.infinitive_device", return_value=device):
        assert await async_setup_component(hass, "climate", {
            "climate": [{"platform": "infinitive", "host": "192.0.2.1", "port": 8080}]
        })
        await hass.async_block_till_done()
        state = hass.states.get("climate.infinitive")
        assert state is not None, "Infinitive failed to create its climate entity"
        assert state.state == "heat"
        assert state.attributes["current_temperature"] == 70
        await hass.services.async_call("climate", "set_temperature", {
            "entity_id": state.entity_id, "temperature": 69,
        }, blocking=True)
        device.set_temp.assert_called_with(69, "heat")
        await hass.services.async_call("climate", "turn_off", {"entity_id": state.entity_id}, blocking=True)
        device.set_mode.assert_called_with("off")
        await hass.services.async_call("climate", "turn_on", {"entity_id": state.entity_id}, blocking=True)
        assert device.set_mode.call_args.args[0] in ("heat", "cool", "auto")
