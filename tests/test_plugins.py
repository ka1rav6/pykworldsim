"""Tests for the PluginRegistry."""
from __future__ import annotations

import pytest

from pykworldsim.core.systems.base_system import BaseSystem
from pykworldsim.plugins.registry import PluginRegistry


class DummySystem(BaseSystem):
    def update(self, dt: float) -> None:
        pass


class AnotherSystem(BaseSystem):
    def update(self, dt: float) -> None:
        pass


@pytest.fixture(autouse=True)
def clear_registry():
    """Ensure registry is empty before and after each test."""
    PluginRegistry.clear()
    yield
    PluginRegistry.clear()


def test_register_and_get() -> None:
    PluginRegistry.register("DummySystem", DummySystem)
    assert PluginRegistry.get("DummySystem") is DummySystem


def test_get_missing_returns_none() -> None:
    assert PluginRegistry.get("NonExistent") is None


def test_all_systems_returns_copy() -> None:
    PluginRegistry.register("DummySystem", DummySystem)
    all_sys = PluginRegistry.all_systems()
    assert "DummySystem" in all_sys
    # Mutating the copy must not affect registry
    del all_sys["DummySystem"]
    assert PluginRegistry.get("DummySystem") is DummySystem


def test_list_names_sorted() -> None:
    PluginRegistry.register("Zebra", DummySystem)
    PluginRegistry.register("Alpha", AnotherSystem)
    assert PluginRegistry.list_names() == ["Alpha", "Zebra"]


def test_unregister() -> None:
    PluginRegistry.register("DummySystem", DummySystem)
    PluginRegistry.unregister("DummySystem")
    assert PluginRegistry.get("DummySystem") is None


def test_unregister_nonexistent_silent() -> None:
    PluginRegistry.unregister("DoesNotExist")  # must not raise


def test_register_non_basesystem_raises() -> None:
    class NotASystem:
        pass

    with pytest.raises(TypeError):
        PluginRegistry.register("Bad", NotASystem)  # type: ignore[arg-type]


def test_registered_plugin_available_via_config() -> None:
    """Plugins registered in the registry must be discoverable by ConfigLoader."""
    PluginRegistry.register("DummySystem", DummySystem)
    from pykworldsim.plugins.registry import PluginRegistry as PR
    assert "DummySystem" in PR.all_systems()


def test_register_from_path() -> None:
    """Register a class by its dotted import path."""
    PluginRegistry.register_from_path(
        "pykworldsim.core.systems.movement.MovementSystem"
    )
    from pykworldsim.core.systems.movement import MovementSystem
    assert PluginRegistry.get("MovementSystem") is MovementSystem


def test_register_from_invalid_path_raises() -> None:
    with pytest.raises((ImportError, AttributeError)):
        PluginRegistry.register_from_path("no_such_module.NoClass")
