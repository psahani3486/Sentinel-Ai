"""
Sentinel AI — Local Plugin Loader

Discovers, parses, and validates local plugin extension manifests.
"""

import logging
from typing import Any

from app.models.enums import PluginStatus
from app.plugins.base_plugin import BasePlugin
from app.plugins.manifest import PluginManifest

logger = logging.getLogger(__name__)


class SampleExtensionPlugin(BasePlugin):
    """Concrete extension plugin strategy used for default built-in SDK extensions."""

    def initialize(self, context: dict[str, Any] | None = None) -> bool:
        self.set_status(PluginStatus.LOADED)
        return True

    def execute(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "status": "success",
            "plugin_id": self.plugin_id,
            "message": f"Plugin '{self.manifest.name}' executed successfully.",
            "payload": payload or {},
        }

    def shutdown(self) -> None:
        self.set_status(PluginStatus.UNLOADED)


class PluginLoader:
    """Discovers, parses, and validates plugin manifests and entry points."""

    def load_from_manifest_data(self, manifest_dict: dict[str, Any]) -> BasePlugin:
        """
        Validate manifest dictionary and instantiate BasePlugin.

        Args:
            manifest_dict: Dictionary containing plugin.yaml fields.

        Returns:
            Validated BasePlugin instance.
        """
        manifest = PluginManifest(**manifest_dict)
        plugin = SampleExtensionPlugin(manifest)
        plugin.set_status(PluginStatus.VALIDATED)
        logger.debug("Successfully validated plugin manifest for '%s'", manifest.id)
        return plugin
