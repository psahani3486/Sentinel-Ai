"""
Sentinel AI — Plugin Engine

Orchestrates plugin discovery, manifest validation, lifecycle transitions, and execution dispatching.
"""

from typing import Any

from app.models.enums import PluginStatus
from app.plugins.base_plugin import BasePlugin
from app.plugins.loader import PluginLoader
from app.plugins.registry import PluginRegistry, get_plugin_registry


class PluginEngine:
    """Orchestrates plugin lifecycle and execution dispatching."""

    def __init__(
        self,
        registry: PluginRegistry | None = None,
        loader: PluginLoader | None = None,
    ) -> None:
        self._registry = registry or get_plugin_registry()
        self._loader = loader or PluginLoader()

    def discover_and_load_plugins(self) -> list[BasePlugin]:
        """Discover and load all registered local plugins."""
        plugins = self._registry.get_all()
        for p in plugins:
            if p.status in (PluginStatus.DISCOVERED, PluginStatus.VALIDATED):
                p.initialize()
                p.set_status(PluginStatus.LOADED)
        return plugins

    def enable_plugin(self, plugin_id: str) -> BasePlugin:
        """Enable a loaded plugin."""
        plugin = self._registry.get(plugin_id)
        if not plugin:
            raise KeyError(f"Plugin '{plugin_id}' not found in registry")
        if plugin.status not in (PluginStatus.LOADED, PluginStatus.DISABLED):
            plugin.initialize()
        plugin.set_status(PluginStatus.ENABLED)
        return plugin

    def disable_plugin(self, plugin_id: str) -> BasePlugin:
        """Disable an active plugin."""
        plugin = self._registry.get(plugin_id)
        if not plugin:
            raise KeyError(f"Plugin '{plugin_id}' not found in registry")
        plugin.set_status(PluginStatus.DISABLED)
        return plugin

    def execute_plugin(self, plugin_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute logic for an enabled plugin."""
        plugin = self._registry.get(plugin_id)
        if not plugin:
            raise KeyError(f"Plugin '{plugin_id}' not found in registry")
        if plugin.status != PluginStatus.ENABLED:
            raise ValueError(f"Plugin '{plugin_id}' is not in ENABLED state (current: {plugin.status.value})")
        return plugin.execute(payload)
