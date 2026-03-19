"""final_performance_optimizations

Revision ID: ddc62c586638
Revises: 8eeccf4c1606
Create Date: 2026-03-18 20:49:52.780849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddc62c586638'
down_revision = '8eeccf4c1606'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Optimized Partial Indexes for Meetings (soft-delete aware)
    op.create_index(
        'idx_meetings_company_active_partial',
        'meetings',
        ['company_id', 'status', 'created_at'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )
    op.create_index(
        'idx_meetings_company_scheduled_partial',
        'meetings',
        ['company_id', 'scheduled_start'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )

    # 2. Optimized Composite Index for Action Items
    op.create_index(
        'idx_action_items_company_filter_composite',
        'action_items',
        ['company_id', 'status', 'priority', 'created_at'],
        unique=False
    )

    # 3. Optimized Composite Index for Calendar Events
    op.create_index(
        'idx_calendar_events_user_start_active',
        'calendar_events',
        ['user_id', 'start_time'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )

    # 4. Restore Meeting Attendees Indexes (if they were dropped)
    op.create_index('idx_meeting_attendees_meeting_id_email', 'meeting_attendees', ['meeting_id', 'email'], if_not_exists=True)
    op.create_index('idx_meeting_attendees_company_id_created', 'meeting_attendees', ['company_id', 'created_at'], if_not_exists=True)


def downgrade() -> None:
    op.drop_index('idx_meeting_attendees_company_id_created', table_name='meeting_attendees')
    op.drop_index('idx_meeting_attendees_meeting_id_email', table_name='meeting_attendees')
    op.drop_index('idx_calendar_events_user_start_active', table_name='calendar_events')
    op.drop_index('idx_action_items_company_filter_composite', table_name='action_items')
    op.drop_index('idx_meetings_company_scheduled_partial', table_name='meetings')
    op.drop_index('idx_meetings_company_active_partial', table_name='meetings')
