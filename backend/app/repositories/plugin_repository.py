"""
Sentinel AI — Plugin Repositories

Repository layer for persisting, querying, and updating Plugin and PluginInstallation entities.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.plugin import Plugin, PluginInstallation
from app.repositories.base import BaseRepository


class PluginRepository(BaseRepository[Plugin]):
    """Repository for managing Plugin entities."""

    def __init__(self, session) -> None:
        super().__init__(Plugin, session)

    async def get_by_plugin_id(self, plugin_id_str: str) -> Plugin | None:
        """Fetch Plugin by unique string plugin_id."""
        stmt = (
            select(Plugin)
            .where(Plugin.plugin_id == plugin_id_str)
            .options(selectinload(Plugin.installations))
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all_plugins(self) -> Sequence[Plugin]:
        """Fetch all plugins ordered by name asc."""
        stmt = (
            select(Plugin)
            .options(selectinload(Plugin.installations))
            .order_by(Plugin.name.asc())
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class PluginInstallationRepository(BaseRepository[PluginInstallation]):
    """Repository for managing PluginInstallation entities."""

    def __init__(self, session) -> None:
        super().__init__(PluginInstallation, session)

    async def get_by_plugin_pk(self, plugin_pk: uuid.UUID) -> PluginInstallation | None:
        """Fetch installation record for a plugin PK."""
        stmt = select(PluginInstallation).where(PluginInstallation.plugin_id == plugin_pk)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()
