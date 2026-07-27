"""
Sentinel AI — Database Initialization & Seeding

Creates the initial admin user on first startup if no admin exists.
Called from the application lifespan handler.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, async_engine
from app.models.base import Base
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


async def seed_admin_user(session: AsyncSession | None = None) -> None:
    """
    Create the initial admin user if one does not already exist.
    """
    settings = get_settings()

    async def _seed(sess: AsyncSession) -> None:
        try:
            result = await sess.execute(
                select(User).where(User.role == UserRole.ADMIN).limit(1)
            )
            existing_admin = result.scalar_one_or_none()

            if existing_admin is not None:
                logger.info("Admin user already exists, skipping seed")
                return

            admin = User(
                email=settings.FIRST_ADMIN_EMAIL,
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
                full_name=settings.FIRST_ADMIN_FULL_NAME,
                role=UserRole.ADMIN,
                is_active=True,
                is_superuser=True,
            )
            sess.add(admin)
            await sess.commit()
            logger.info("Seeded initial admin user: %s", settings.FIRST_ADMIN_EMAIL)
        except Exception as e:
            logger.warning("Seed admin user skipped or caught exception: %s", str(e))

    if session is not None:
        await _seed(session)
    else:
        try:
            async with AsyncSessionLocal() as sess:
                await _seed(sess)
        except Exception as e:
            logger.warning("AsyncSessionLocal initialization skipped: %s", str(e))


async def init_db(session: AsyncSession | None = None) -> None:
    """Run all database initialization tasks."""
    settings = get_settings()
    if settings.DATABASE_URL.startswith("sqlite"):
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    await seed_admin_user(session=session)
