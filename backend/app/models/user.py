"""
Sentinel AI — User Model

Defines the User table and the UserRole enum.
This is the only authentication-related model for Phase 1.
"""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, enum.Enum):
    """
    Role-Based Access Control roles.

    - ADMIN: Full platform access, user management.
    - DATA_ENGINEER: Pipeline and data quality management.
    - ML_ENGINEER: Model training and monitoring.
    - VIEWER: Read-only access to dashboards and reports.
    """

    ADMIN = "admin"
    DATA_ENGINEER = "data_engineer"
    ML_ENGINEER = "ml_engineer"
    VIEWER = "viewer"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Sentinel AI user account.

    Stores authentication credentials and RBAC role assignment.
    Supports soft-delete via the is_active flag.
    """

    __tablename__ = "users"

    __table_args__ = (
        Index("ix_users_created_at", "created_at"),
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=UserRole.VIEWER,
        server_default=UserRole.VIEWER.value,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
        index=True,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
