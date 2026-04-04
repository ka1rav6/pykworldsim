"""PluginRegistry — register and discover custom ECS systems at runtime."""
from __future__ import annotations

import importlib
import logging
from typing import Any, Type

from pykworldsim.core.systems.base_system import BaseSystem

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, Type[BaseSystem]] = {}


class PluginRegistry:
    """
    Global registry for dynamically loaded ECS systems.

    Users can register their own systems so they become available
    by name in YAML/JSON configs and via the CLI.

    Examples
    --------
    Register a class directly::

        from pykworldsim.plugins import PluginRegistry
        from mypackage.systems import MyCustomSystem

        PluginRegistry.register("MyCustomSystem", MyCustomSystem)

    Register via dotted import path (useful in config files)::

        PluginRegistry.register_from_path("mypackage.systems.MyCustomSystem")

    Use in a config::

        systems:
          - type: MyCustomSystem

    Discover all registered systems::

        all_sys = PluginRegistry.all_systems()   # {"MyCustomSystem": <class>}
    """

    @staticmethod
    def register(name: str, system_class: Type[BaseSystem]) -> None:
        """
        Register *system_class* under *name*.

        Raises
        ------
        TypeError
            If *system_class* is not a subclass of :class:`BaseSystem`.
        """
        if not (isinstance(system_class, type) and issubclass(system_class, BaseSystem)):
            raise TypeError(
                f"{system_class!r} is not a subclass of BaseSystem."
            )
        _REGISTRY[name] = system_class
        logger.info("Plugin registered: %r → %s", name, system_class.__qualname__)

    @staticmethod
    def register_from_path(dotted_path: str) -> None:
        """
        Import and register a system class from a dotted module path.

        Parameters
        ----------
        dotted_path:
            E.g. ``"mypackage.systems.MyCustomSystem"``.

        Raises
        ------
        ImportError / AttributeError
            If the path cannot be resolved.
        """
        module_path, _, class_name = dotted_path.rpartition(".")
        if not module_path:
            raise ImportError(f"Invalid dotted path: {dotted_path!r}")
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        PluginRegistry.register(class_name, cls)

    @staticmethod
    def unregister(name: str) -> None:
        """Remove *name* from the registry. Silent if not found."""
        _REGISTRY.pop(name, None)

    @staticmethod
    def get(name: str) -> Type[BaseSystem] | None:
        """Return the system class registered as *name*, or ``None``."""
        return _REGISTRY.get(name)

    @staticmethod
    def all_systems() -> dict[str, Type[BaseSystem]]:
        """Return a copy of all currently registered plugin systems."""
        return dict(_REGISTRY)

    @staticmethod
    def clear() -> None:
        """Clear all registered plugins (mainly useful in tests)."""
        _REGISTRY.clear()

    @staticmethod
    def list_names() -> list[str]:
        """Return a sorted list of all registered system names."""
        return sorted(_REGISTRY.keys())
