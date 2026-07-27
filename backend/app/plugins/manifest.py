"""
Sentinel AI — Plugin Manifest Specification

Pydantic model defining strict schema validation rules for plugin.yaml files.
"""

from typing import Any
from pydantic import BaseModel, Field, field_validator

from app.models.enums import PluginType


class PluginManifest(BaseModel):
    """Pydantic model validating plugin.yaml metadata."""

    id: str = Field(description="Unique plugin ID string, e.g. sentinel.plugin.csv_pro")
    name: str = Field(description="Human readable plugin name")
    version: str = Field(default="1.0.0", description="Semantic version string")
    author: str = Field(default="Sentinel AI Extensions Community")
    description: str = Field(default="Custom extension plugin for Sentinel AI platform")
    plugin_type: PluginType = Field(description="Plugin type categorization enum")
    entry_point: str = Field(description="Python entry point module or class name")
    minimum_platform_version: str = Field(default="1.0.0")
    permissions: list[str] = Field(default_factory=list, description="Declared platform permissions")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def validate_plugin_id(cls, v: str) -> str:
        if not v or "." not in v:
            raise ValueError("Plugin ID must be namespaced with at least one dot (e.g. 'sentinel.plugin.custom')")
        return v
