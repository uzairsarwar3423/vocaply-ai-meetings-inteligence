"""Add performance indexes to frequently queried columns

Revision ID: add_performance_indexes
Revises: a3344e86605e
Create Date: 2026-02-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = 'a3344e86605e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add indexes for frequently queried columns"""
    
    # Action Items - frequently filtered by status, priority, assignee, meeting
    op.create_index(
        op.f('ix_action_items_status_created_at'),
        'action_items',
        ['status', 'created_at'],
        unique=False,
        if_not_exists=True,
    )
    
    op.create_index(
        op.f('ix_action_items_priority_status'),
        'action_items',
        ['priority', 'status'],
        unique=False,
        if_not_exists=True,
    )
    
    op.create_index(
        op.f('ix_action_items_assigned_to_id_status'),
        'action_items',
        ['assigned_to_id', 'status'],
        unique=False,
        if_not_exists=True,
    )
    
    op.create_index(
        op.f('ix_action_items_due_date'),
        'action_items',
        ['due_date'],
        unique=False,
        if_not_exists=True,
    )
    
    # Meetings - frequently filtered by status, created_at, platform
    op.create_index(
        op.f('ix_meetings_status_created_at'),
        'meetings',
        ['status', 'created_at'],
        unique=False,
        if_not_exists=True,
    )
    
    op.create_index(
        op.f('ix_meetings_platform_created_at'),
        'meetings',
        ['platform', 'created_at'],
        unique=False,
        if_not_exists=True,
    )
    
    op.create_index(
        op.f('ix_meetings_scheduled_start'),
        'meetings',
        ['scheduled_start'],
        unique=False,
        if_not_exists=True,
    )
    
    # Transcripts - frequently searched and filtered by meeting
    op.create_index(
        op.f('ix_transcripts_meeting_id_created_at'),
        'transcripts',
        ['meeting_id', 'created_at'],
        unique=False,
        if_not_exists=True,
    )
    
    op.create_index(
        op.f('ix_transcripts_speaker_id'),
        'transcripts',
        ['speaker_id'],
        unique=False,
        if_not_exists=True,
    )
    
    # User Sessions - frequently accessed for auth
    op.create_index(
        op.f('ix_user_sessions_user_id_created_at'),
        'user_sessions',
        ['user_id', 'created_at'],
        unique=False,
        if_not_exists=True,
    )
    
    # AI Usage - frequently aggregated by company and date
    op.create_index(
        op.f('ix_ai_usage_company_id_created_at'),
        'ai_usage',
        ['company_id', 'created_at'],
        unique=False,
        if_not_exists=True,
    )
    
    op.create_index(
        op.f('ix_ai_usage_feature_type'),
        'ai_usage',
        ['feature_type'],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    """Remove performance indexes"""
    
    op.drop_index(op.f('ix_ai_usage_feature_type'), table_name='ai_usage')
    op.drop_index(op.f('ix_ai_usage_company_id_created_at'), table_name='ai_usage')
    op.drop_index(op.f('ix_user_sessions_user_id_created_at'), table_name='user_sessions')
    op.drop_index(op.f('ix_transcripts_speaker_id'), table_name='transcripts')
    op.drop_index(op.f('ix_transcripts_meeting_id_created_at'), table_name='transcripts')
    op.drop_index(op.f('ix_meetings_scheduled_start'), table_name='meetings')
    op.drop_index(op.f('ix_meetings_platform_created_at'), table_name='meetings')
    op.drop_index(op.f('ix_meetings_status_created_at'), table_name='meetings')
    op.drop_index(op.f('ix_action_items_due_date'), table_name='action_items')
    op.drop_index(op.f('ix_action_items_assigned_to_id_status'), table_name='action_items')
    op.drop_index(op.f('ix_action_items_priority_status'), table_name='action_items')
    op.drop_index(op.f('ix_action_items_status_created_at'), table_name='action_items')
