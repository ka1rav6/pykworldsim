"""Tests for PluginRegistry."""
from __future__ import annotations
import pytest
from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.plugins.registry import PluginRegistry


class DummySystem(BaseSystem):
    def update(self, world, dt): pass

class AnotherSystem(BaseSystem):
    def update(self, world, dt): pass


def test_register_get():
    PluginRegistry.register("DummySystem", DummySystem)
    assert PluginRegistry.get("DummySystem") is DummySystem

def test_get_missing_returns_none():
    assert PluginRegistry.get("Missing") is None

def test_all_systems_copy():
    PluginRegistry.register("DummySystem", DummySystem)
    all_s = PluginRegistry.all_systems()
    del all_s["DummySystem"]
    assert PluginRegistry.get("DummySystem") is DummySystem

def test_list_names_sorted():
    PluginRegistry.register("Zebra", DummySystem)
    PluginRegistry.register("Alpha", AnotherSystem)
    assert PluginRegistry.list_names() == ["Alpha", "Zebra"]

def test_unregister():
    PluginRegistry.register("DummySystem", DummySystem)
    PluginRegistry.unregister("DummySystem")
    assert PluginRegistry.get("DummySystem") is None

def test_unregister_nonexistent_silent():
    PluginRegistry.unregister("DoesNotExist")  # no raise

def test_register_non_basesystem_raises():
    class Bad: pass
    with pytest.raises(TypeError):
        PluginRegistry.register("Bad", Bad)  # type: ignore[arg-type]

def test_register_from_path():
    PluginRegistry.register_from_path("pykworldsim.core.systems.movement.MovementSystem")
    from pykworldsim.core.systems.movement import MovementSystem
    assert PluginRegistry.get("MovementSystem") is MovementSystem

def test_register_from_invalid_path_raises():
    with pytest.raises((ImportError, AttributeError)):
        PluginRegistry.register_from_path("no_such_module.NoClass")

def test_plugin_available_in_config_build():
    PluginRegistry.register("DummySystem", DummySystem)
    assert "DummySystem" in PluginRegistry.all_systems()
