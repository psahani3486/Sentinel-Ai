"""
Sentinel AI — Core Configuration Alias

Provides settings and Settings singleton for app.core.config.
"""

from app.config.settings import Settings, get_settings

settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
