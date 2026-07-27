"""phase3a_background_jobs

Revision ID: 003_phase3a_background_jobs
Revises: 002_phase2a_database_foundation
Create Date: 2026-07-26 18:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_phase3a_background_jobs'
down_revision: Union[str, None] = '002_phase2a_database_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Create Enums ──────────────────────────────────────────────────────────
    job_status_enum = postgresql.ENUM('pending', 'queued', 'running', 'completed', 'failed', 'cancelled', name='job_status', create_type=False)
    job_type_enum = postgresql.ENUM('dataset_upload', 'data_profiling', 'data_validation', name='job_type', create_type=False)
    job_priority_enum = postgresql.ENUM('low', 'medium', 'high', 'critical', name='job_priority', create_type=False)

    sa.Enum('pending', 'queued', 'running', 'completed', 'failed', 'cancelled', name='job_status').create(op.get_bind(), checkfirst=True)
    sa.Enum('dataset_upload', 'data_profiling', 'data_validation', name='job_type').create(op.get_bind(), checkfirst=True)
    sa.Enum('low', 'medium', 'high', 'critical', name='job_priority').create(op.get_bind(), checkfirst=True)

    # ── Create jobs table ─────────────────────────────────────────────────────
    op.create_table(
        'jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('job_type', job_type_enum, nullable=False),
        sa.Column('status', job_status_enum, server_default='pending', nullable=False),
        sa.Column('priority', job_priority_enum, server_default='medium', nullable=False),
        sa.Column('progress_percentage', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('latest_message', sa.String(length=512), nullable=True),
        sa.Column('dataset_id', sa.UUID(), nullable=True),
        sa.Column('dataset_version_id', sa.UUID(), nullable=True),
        sa.Column('validation_run_id', sa.UUID(), nullable=True),
        sa.Column('created_by_id', sa.UUID(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_time_ms', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('max_retries', sa.Integer(), server_default='3', nullable=False),
        sa.Column('job_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dataset_version_id'], ['dataset_versions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['validation_run_id'], ['validation_runs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_jobs_job_type', 'jobs', ['job_type'], unique=False)
    op.create_index('ix_jobs_status', 'jobs', ['status'], unique=False)
    op.create_index('ix_jobs_priority', 'jobs', ['priority'], unique=False)
    op.create_index('ix_jobs_dataset_id', 'jobs', ['dataset_id'], unique=False)
    op.create_index('ix_jobs_created_at', 'jobs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_jobs_created_at', table_name='jobs')
    op.drop_index('ix_jobs_dataset_id', table_name='jobs')
    op.drop_index('ix_jobs_priority', table_name='jobs')
    op.drop_index('ix_jobs_status', table_name='jobs')
    op.drop_index('ix_jobs_job_type', table_name='jobs')
    op.drop_table('jobs')

    op.execute('DROP TYPE IF EXISTS job_priority')
    op.execute('DROP TYPE IF EXISTS job_type')
    op.execute('DROP TYPE IF EXISTS job_status')
