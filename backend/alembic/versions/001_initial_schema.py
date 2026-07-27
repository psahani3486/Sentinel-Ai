"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-07-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum('admin', 'data_engineer', 'ml_engineer', 'viewer', name='user_role').create(op.get_bind(), checkfirst=True)
    user_role_enum = postgresql.ENUM('admin', 'data_engineer', 'ml_engineer', 'viewer', name='user_role', create_type=False)
    
    # ── Create users Table ──────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', user_role_enum, server_default='viewer', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_superuser', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes on users
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_role', 'users', ['role'], unique=False)
    op.create_index('ix_users_is_active', 'users', ['is_active'], unique=False)
    op.create_index('ix_users_created_at', 'users', ['created_at'], unique=False)

    # ── Create user_refresh_tokens Table ────────────────────────────────────
    op.create_table(
        'user_refresh_tokens',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('jti', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes on user_refresh_tokens
    op.create_index('ix_user_refresh_tokens_user_id', 'user_refresh_tokens', ['user_id'], unique=False)
    op.create_index('ix_user_refresh_tokens_jti', 'user_refresh_tokens', ['jti'], unique=True)
    op.create_index('ix_user_refresh_tokens_is_revoked', 'user_refresh_tokens', ['is_revoked'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_user_refresh_tokens_is_revoked', table_name='user_refresh_tokens')
    op.drop_index('ix_user_refresh_tokens_jti', table_name='user_refresh_tokens')
    op.drop_index('ix_user_refresh_tokens_user_id', table_name='user_refresh_tokens')
    op.drop_table('user_refresh_tokens')
    
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    
    # Drop user_role enum
    sa.Enum(name='user_role').drop(op.get_bind(), checkfirst=False)
