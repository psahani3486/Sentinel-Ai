"""
Sentinel AI — Plugin Reporter

Formats plugin health metrics and permission audits for UI rendering.
"""

from typing import Any


class PluginReporter:
    """Formats plugin status and permissions for UI management dashboard."""

    def build_dashboard_summary(self, plugins: list[Any]) -> dict[str, Any]:
        """Build plugin ecosystem summary."""
        enabled_cnt = 0
        disabled_cnt = 0
        total = len(plugins)

        for p in plugins:
            st = str(getattr(p, "status", "discovered")).lower()
            if st == "enabled":
                enabled_cnt += 1
            elif st == "disabled":
                disabled_cnt += 1

        return {
            "total_plugins": total,
            "enabled_plugins_count": enabled_cnt,
            "disabled_plugins_count": disabled_cnt,
            "latest_plugin": plugins[0] if plugins else None,
        }
