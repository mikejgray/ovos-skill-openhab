# pylint: disable=missing-docstring
from threading import Event
from unittest.mock import Mock
import pytest
from ovos_skill_openhab import openHABSkill
from ovos_plugin_manager.skills import find_skill_plugins
from ovos_utils.fakebus import FakeBus
# TODO: Mock settings path, set up fixtures


def test_skill_is_a_valid_plugin():
    assert "ovos-skill-openhab.mikejgray" in find_skill_plugins().keys()


def test_no_config_calls_speak_dialog():
    fake_bus = FakeBus()
    fake_bus.emitter = fake_bus.ee
    fake_bus.connected_event = Event()
    fake_bus.connected_event.set()
    fake_bus.run_forever()
    skill = openHABSkill(bus=fake_bus, settings={"host": "", "port": ""}, skill_id="ovos-skill-openhab.mikejgray")
    skill.speak_dialog = Mock()
    skill.speak_dialog.assert_called_with({})


def test_list_all_devices_from_demo():
    fake_bus = FakeBus()
    fake_bus.emitter = fake_bus.ee
    fake_bus.connected_event = Event()
    fake_bus.connected_event.set()
    fake_bus.run_forever()
    skill = openHABSkill(bus=fake_bus, settings={"host": "localhost", "port": "8080"}, skill_id="ovos-skill-openhab.mikejgray")
    skill.speak_dialog = Mock()
    skill.speak_dialog.assert_not_called()


if __name__ == "__main__":
    pytest.main()
