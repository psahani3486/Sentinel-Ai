"""
Sentinel AI — Base Plugin Strategy Interface

Abstract strategy interface for local third-party extension plugins.
"""

import abc
from typing import Any

from app.models.enums import PluginStatus, PluginType
from app.plugins.manifest import PluginManifest


class BasePlugin(abc.ABC):
    """Abstract strategy interface implemented by all Sentinel AI extension plugins."""

    def __init__(self, manifest: PluginManifest) -> None:
        self._manifest = manifest
        self._status = PluginStatus.DISCOVERED

    @property
    def manifest(self) -> PluginManifest:
        """Return plugin manifest metadata."""
        return self._manifest

    @property
    def plugin_id(self) -> str:
        """Return plugin unique ID."""
        return self._manifest.id

    @property
    def plugin_type(self) -> PluginType:
        """Return plugin type enum."""
        return self._manifest.plugin_type

    @property
    def status(self) -> PluginStatus:
        """Return current lifecycle status of plugin."""
        return self._status

    def set_status(self, status: PluginStatus) -> None:
        """Update plugin lifecycle status."""
        self._status = status

    @abc.abstractmethod
    def initialize(self, context: dict[str, Any] | None = None) -> bool:
        """Initialize plugin resources."""
        pass

    @abc.abstractmethod
    def execute(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute plugin logic."""
        pass

    @abc.abstractmethod
    def shutdown(self) -> None:
        """Release plugin resources on unload."""
        pass
