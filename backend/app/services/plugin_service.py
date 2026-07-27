"""
Sentinel AI — Plugin Service

Service layer managing local plugin discovery, manifest validation, lifecycle transitions,
and database persistence.
"""

import logging
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PluginStatus
from app.models.plugin import Plugin, PluginInstallation
from app.plugins.engine import PluginEngine
from app.repositories.plugin_repository import (
    PluginInstallationRepository,
    PluginRepository,
)

logger = logging.getLogger(__name__)


class PluginService:
    """Coordinates plugin discovery, lifecycle state transitions, and database sync."""

    def __init__(
        self,
        db_session: AsyncSession,
        plugin_repo: PluginRepository | None = None,
        inst_repo: PluginInstallationRepository | None = None,
        engine: PluginEngine | None = None,
    ) -> None:
        self._session = db_session
        self._plugin_repo = plugin_repo or PluginRepository(db_session)
        self._inst_repo = inst_repo or PluginInstallationRepository(db_session)
        self._engine = engine or PluginEngine()

    async def discover_plugins(self) -> Sequence[Plugin]:
        """Discover local plugins from registry and sync with database."""
        reg_plugins = self._engine.discover_and_load_plugins()

        for p_strat in reg_plugins:
            m = p_strat.manifest
            existing = await self._plugin_repo.get_by_plugin_id(m.id)
            if not existing:
                p_entity = Plugin(
                    plugin_id=m.id,
                    name=m.name,
                    version=m.version,
                    author=m.author,
                    description=m.description,
                    plugin_type=m.plugin_type,
                    status=p_strat.status,
                    entry_point=m.entry_point,
                    minimum_platform_version=m.minimum_platform_version,
                    permissions={"permissions": m.permissions},
                    manifest_data=m.model_dump(),
                )
                p_entity = await self._plugin_repo.create(p_entity)

                # Create installation record
                inst = PluginInstallation(
                    plugin_id=p_entity.id,
                    installed_by="system",
                    is_enabled=False,
                )
                await self._inst_repo.create(inst)

        return await self._plugin_repo.get_all_plugins()

    async def get_all(self) -> Sequence[Plugin]:
        """Fetch all registered plugins."""
        plugins = await self._plugin_repo.get_all_plugins()
        if not plugins:
            return await self.discover_plugins()
        return plugins

    async def get_by_id(self, plugin_id_str: str) -> Plugin | None:
        """Fetch plugin by unique string plugin_id."""
        return await self._plugin_repo.get_by_plugin_id(plugin_id_str)

    async def enable_plugin(self, plugin_id_str: str) -> Plugin:
        """Enable a plugin strategy and update database status."""
        p_entity = await self._plugin_repo.get_by_plugin_id(plugin_id_str)
        if not p_entity:
            raise KeyError(f"Plugin '{plugin_id_str}' not found in database")

        self._engine.enable_plugin(plugin_id_str)
        await self._plugin_repo.update(p_entity, {"status": PluginStatus.ENABLED})

        inst = await self._inst_repo.get_by_plugin_pk(p_entity.id)
        if inst:
            await self._inst_repo.update(inst, {"is_enabled": True})

        logger.info("Enabled Plugin '%s'", plugin_id_str)
        return p_entity

    async def disable_plugin(self, plugin_id_str: str) -> Plugin:
        """Disable a plugin strategy and update database status."""
        p_entity = await self._plugin_repo.get_by_plugin_id(plugin_id_str)
        if not p_entity:
            raise KeyError(f"Plugin '{plugin_id_str}' not found in database")

        self._engine.disable_plugin(plugin_id_str)
        await self._plugin_repo.update(p_entity, {"status": PluginStatus.DISABLED})

        inst = await self._inst_repo.get_by_plugin_pk(p_entity.id)
        if inst:
            await self._inst_repo.update(inst, {"is_enabled": False})

        logger.info("Disabled Plugin '%s'", plugin_id_str)
        return p_entity

    async def reload_plugins(self) -> Sequence[Plugin]:
        """Reload all local plugins."""
        return await self.discover_plugins()
