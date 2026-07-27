"""
Sentinel AI — Plugin Strategy Registry

Registry Pattern maintaining instances of all discovered local plugins.
"""

import logging

from app.models.enums import PluginType
from app.plugins.base_plugin import BasePlugin
from app.plugins.loader import PluginLoader

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Registry maintaining active extension plugin strategy instances."""

    def __init__(self) -> None:
        self._plugins: dict[str, BasePlugin] = {}
        self._loader = PluginLoader()
        self._register_default_sdk_plugins()

    def _register_default_sdk_plugins(self) -> None:
        """Register default built-in SDK example plugins."""
        sdk_manifests = [
            {
                "id": "sentinel.plugin.connector.snowflake",
                "name": "Snowflake Cloud Connector",
                "version": "1.2.0",
                "author": "Sentinel AI SDK Team",
                "description": "High throughput Snowflake ingestion connector plugin.",
                "plugin_type": PluginType.CONNECTOR,
                "entry_point": "examples.connector_plugin.main:SnowflakeConnectorPlugin",
                "minimum_platform_version": "1.0.0",
                "permissions": ["network:read", "database:connect"],
            },
            {
                "id": "sentinel.plugin.rule.regex_anomaly",
                "name": "Regex Anomaly Validation Rule",
                "version": "1.0.1",
                "author": "Sentinel AI SDK Team",
                "description": "Custom regex string pattern validation rule plugin.",
                "plugin_type": PluginType.VALIDATION_RULE,
                "entry_point": "examples.validation_plugin.main:RegexAnomalyRulePlugin",
                "minimum_platform_version": "1.0.0",
                "permissions": ["data:read"],
            },
            {
                "id": "sentinel.plugin.workflow.multi_cloud",
                "name": "Multi-Cloud Ingestion Pipeline",
                "version": "2.0.0",
                "author": "Sentinel AI SDK Team",
                "description": "Multi-cloud pipeline orchestrator workflow plugin.",
                "plugin_type": PluginType.WORKFLOW,
                "entry_point": "examples.workflow_plugin.main:MultiCloudWorkflowPlugin",
                "minimum_platform_version": "1.0.0",
                "permissions": ["workflow:execute", "job:create"],
            },
        ]

        for mdata in sdk_manifests:
            p = self._loader.load_from_manifest_data(mdata)
            self.register(p)

    def register(self, plugin: BasePlugin) -> None:
        """Register a plugin strategy."""
        self._plugins[plugin.plugin_id] = plugin
        logger.debug("Registered Plugin: %s (%s)", plugin.plugin_id, plugin.plugin_type.value)

    def get(self, plugin_id: str) -> BasePlugin | None:
        """Retrieve plugin strategy by plugin_id."""
        return self._plugins.get(plugin_id)

    def get_by_type(self, plugin_type: PluginType) -> list[BasePlugin]:
        """Retrieve all plugins matching a PluginType."""
        return [p for p in self._plugins.values() if p.plugin_type == plugin_type]

    def get_all(self) -> list[BasePlugin]:
        """Return list of all registered plugins."""
        return list(self._plugins.values())


# Global default registry singleton
_default_registry: PluginRegistry | None = None


def get_plugin_registry() -> PluginRegistry:
    """Return singleton PluginRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = PluginRegistry()
    return _default_registry
