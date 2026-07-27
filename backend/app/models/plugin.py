"""
Sentinel AI — Plugin Orchestration Models

SQLAlchemy ORM models representing local plugin extensions (Plugin)
and plugin installations (PluginInstallation).
"""

import datetime
import uuid
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import PluginStatus, PluginType


class Plugin(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents a local extension plugin in Sentinel AI.
    """

    __tablename__ = "plugins"

    __table_args__ = (
        Index("ix_plugins_plugin_id", "plugin_id", unique=True),
        Index("ix_plugins_plugin_type", "plugin_type"),
        Index("ix_plugins_status", "status"),
        Index("ix_plugins_created_at", "created_at"),
    )

    plugin_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    author: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    plugin_type: Mapped[PluginType] = mapped_column(
        Enum(PluginType, name="plugin_type", create_constraint=True),
        nullable=False,
    )
    status: Mapped[PluginStatus] = mapped_column(
        Enum(PluginStatus, name="plugin_status", create_constraint=True),
        default=PluginStatus.DISCOVERED,
        nullable=False,
    )
    entry_point: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    minimum_platform_version: Mapped[str] = mapped_column(
        String(64),
        default="1.0.0",
        nullable=False,
    )
    permissions: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    manifest_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    installations: Mapped[list["PluginInstallation"]] = relationship(
        "PluginInstallation",
        back_populates="plugin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Plugin(id={self.id}, plugin_id='{self.plugin_id}', status='{self.status.value}')>"


class PluginInstallation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents an installation instance of a plugin.
    """

    __tablename__ = "plugin_installations"

    __table_args__ = (
        Index("ix_plugin_installations_plugin_id", "plugin_id"),
        Index("ix_plugin_installations_created_at", "created_at"),
    )

    plugin_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plugins.id", ondelete="CASCADE"),
        nullable=False,
    )
    installed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )
    installed_by: Mapped[str] = mapped_column(
        String(255),
        default="system",
        nullable=False,
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    configuration: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    plugin: Mapped["Plugin"] = relationship("Plugin", back_populates="installations")

    def __repr__(self) -> str:
        return f"<PluginInstallation(id={self.id}, plugin_id={self.plugin_id}, enabled={self.is_enabled})>"
