"""Use real Home Assistant APIs with a fake Infinitive device."""
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock

import pytest
import pytest_asyncio
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntries
from homeassistant import loader
from homeassistant.helpers import entity_registry, device_registry
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM


@pytest.fixture
def device():
    status = {
        "mode": "heat", "heatSetpoint": 68, "coolSetpoint": 75,
        "currentTemp": 70, "currentHumidity": 42, "targetHumidity": 45,
        "fanMode": "auto", "hold": False, "stage": 1,
        "blowerRPM": 800, "airFlowCFM": 900, "holdDurationMins": 120,
        "outdoorTemp": 50, "auxHeat": False,
    }
    fake = Mock()
    fake.status = status
    fake.get_status.side_effect = lambda: deepcopy(fake.status)
    return fake


@pytest_asyncio.fixture
async def hass(tmp_path):
    # Discover the actual custom integration using HA's loader.
    (tmp_path / "custom_components").symlink_to(
        Path(__file__).resolve().parents[1] / "custom_components",
        target_is_directory=True,
    )
    instance = HomeAssistant(str(tmp_path))
    instance.config.units = US_CUSTOMARY_SYSTEM
    instance.config.skip_pip = True  # Dependencies are installed before tests.
    instance.config_entries = ConfigEntries(instance, {})
    loader.async_setup(instance)
    device_registry.async_setup(instance)
    await device_registry.async_load(instance)
    await entity_registry.async_load(instance)
    try:
        yield instance
    finally:
        await instance.async_stop(force=True)
