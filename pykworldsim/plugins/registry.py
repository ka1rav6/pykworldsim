"""PluginRegistry — register and discover custom ECS systems at runtime."""
from __future__ import annotations
import importlib, logging
from typing import Type
from pykworldsim.core.systems.base_system import BaseSystem

logger = logging.getLogger(__name__)
_REGISTRY: dict[str, Type[BaseSystem]] = {}

class PluginRegistry:
    """Global registry for dynamically loaded ECS systems."""

    @staticmethod
    def register(name: str, system_class: Type[BaseSystem]) -> None:
        if not (isinstance(system_class, type) and issubclass(system_class, BaseSystem)):
            raise TypeError(f"{system_class!r} is not a subclass of BaseSystem.")
        _REGISTRY[name] = system_class
        logger.info("Plugin registered: %r → %s", name, system_class.__qualname__)

    @staticmethod
    def register_from_path(dotted_path: str) -> None:
        module_path, _, class_name = dotted_path.rpartition(".")
        if not module_path:
            raise ImportError(f"Invalid dotted path: {dotted_path!r}")
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        PluginRegistry.register(class_name, cls)

    @staticmethod
    def unregister(name: str) -> None:
        _REGISTRY.pop(name, None)

    @staticmethod
    def get(name: str) -> Type[BaseSystem] | None:
        return _REGISTRY.get(name)

    @staticmethod
    def all_systems() -> dict[str, Type[BaseSystem]]:
        return dict(_REGISTRY)

    @staticmethod
    def clear() -> None:
        _REGISTRY.clear()

    @staticmethod
    def list_names() -> list[str]:
        return sorted(_REGISTRY.keys())
