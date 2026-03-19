"""
Database Schema Optimization - Phase 1
Vocaply Platform - Database Design Improvements

This migration addresses the over-normalized meeting model and adds proper
indexing, partitioning, and normalization for scale.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'db_optimization_phase1'
down_revision = '411832818d32'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Database optimization improvements:

    1. Create meeting_attendees table (normalize attendees from JSONB)
    2. Add composite indexes for complex queries
    3. Add table partitioning for high-volume tables
    4. Optimize existing indexes
    5. Add constraints and validations
    """

    # ============================================
    # 1. CREATE MEETING ATTENDEES TABLE
    # ============================================
    # Normalize attendees from JSONB to proper relational table

    op.create_table(
        'meeting_attendees',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('company_id', sa.String, sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),

        # Attendee info
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('role', sa.String(50), nullable=False, default='attendee'),  # organizer, attendee

        # User linkage (if registered)
        sa.Column('user_id', sa.String, sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),

        # Participation tracking
        sa.Column('joined_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('left_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('is_present', sa.Boolean, nullable=False, default=False),

        # Metadata
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )

    # Indexes for meeting_attendees
    op.create_index('idx_meeting_attendees_meeting_email', 'meeting_attendees', ['meeting_id', 'email'], unique=True, if_not_exists=True)
    op.create_index('idx_meeting_attendees_user', 'meeting_attendees', ['user_id'], if_not_exists=True)
    op.create_index('idx_meeting_attendees_company', 'meeting_attendees', ['company_id', 'created_at'], if_not_exists=True)

    # ============================================
    # 2. ADD COMPOSITE INDEXES FOR COMPLEX QUERIES
    # ============================================

    # Meeting queries - most common patterns
    op.create_index('idx_meetings_company_status_created', 'meetings', ['company_id', 'status', 'created_at'], if_not_exists=True)
    op.create_index('idx_meetings_company_platform', 'meetings', ['company_id', 'platform', 'created_at'], if_not_exists=True)
    op.create_index('idx_meetings_scheduled_range', 'meetings', ['company_id', 'scheduled_start', 'scheduled_end'], if_not_exists=True)
    op.create_index('idx_meetings_creator_status', 'meetings', ['created_by', 'status', 'created_at'], if_not_exists=True)

    # Transcript queries - search and timeline
    op.create_index('idx_transcripts_meeting_time', 'transcripts', ['meeting_id', 'start_time', 'end_time'], if_not_exists=True)
    op.create_index('idx_transcripts_speaker', 'transcripts', ['meeting_id', 'speaker_email', 'start_time'], if_not_exists=True)
    op.create_index('idx_transcripts_company_created', 'transcripts', ['company_id', 'created_at'], if_not_exists=True)
    op.execute("CREATE INDEX IF NOT EXISTS idx_transcripts_search ON transcripts USING gin (text gin_trgm_ops)")

    # Action items queries
    op.create_index('idx_action_items_company_status', 'action_items', ['company_id', 'status', 'created_at'], if_not_exists=True)
    op.create_index('idx_action_items_assigned_due', 'action_items', ['assigned_to_id', 'due_date', 'status'], if_not_exists=True)
    op.create_index('idx_action_items_meeting_status', 'action_items', ['meeting_id', 'status'], if_not_exists=True)
    op.create_index('idx_action_items_priority_status', 'action_items', ['company_id', 'priority', 'status', 'created_at'], if_not_exists=True)

    # User sessions - cleanup and security
    op.create_index('idx_user_sessions_user_created', 'user_sessions', ['user_id', 'created_at'], if_not_exists=True)
    op.create_index('idx_user_sessions_expires', 'user_sessions', ['expires_at'], if_not_exists=True)  # For cleanup jobs

    # ============================================
    # 3. TABLE PARTITIONING — SKIPPED
    # ============================================
    # The transcripts table in this environment is not a partitioned table.
    # Partitioning must be set up during initial table creation (CREATE TABLE ... PARTITION BY).
    # Skipping this step to keep the migration idempotent.
    pass


    # ============================================
    # 4. ADD CONSTRAINTS AND VALIDATIONS
    # ============================================

    # Status transition constraints (using triggers)
    op.execute("""
        CREATE OR REPLACE FUNCTION check_meeting_status_transition()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Valid transitions for meetings
            IF OLD.status = 'scheduled' AND NEW.status NOT IN ('in_progress', 'cancelled') THEN
                RAISE EXCEPTION 'Invalid status transition from % to %', OLD.status, NEW.status;
            ELSIF OLD.status = 'in_progress' AND NEW.status NOT IN ('transcribing', 'completed', 'failed') THEN
                RAISE EXCEPTION 'Invalid status transition from % to %', OLD.status, NEW.status;
            ELSIF OLD.status = 'transcribing' AND NEW.status NOT IN ('analyzing', 'failed') THEN
                RAISE EXCEPTION 'Invalid status transition from % to %', OLD.status, NEW.status;
            ELSIF OLD.status = 'analyzing' AND NEW.status NOT IN ('completed', 'failed') THEN
                RAISE EXCEPTION 'Invalid status transition from % to %', OLD.status, NEW.status;
            ELSIF OLD.status IN ('completed', 'cancelled') THEN
                RAISE EXCEPTION 'Cannot change status from terminal state %', OLD.status;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        DROP TRIGGER IF EXISTS meeting_status_transition_trigger ON meetings;
        CREATE TRIGGER meeting_status_transition_trigger
            BEFORE UPDATE ON meetings
            FOR EACH ROW
            WHEN (OLD.status IS DISTINCT FROM NEW.status)
            EXECUTE FUNCTION check_meeting_status_transition();
    """)

    # ============================================
    # 5. MIGRATE EXISTING DATA
    # ============================================
    # Migrate attendees from JSONB to normalized table

    op.execute("""
        INSERT INTO meeting_attendees (
            meeting_id, company_id, email, name, role, user_id, joined_at, left_at, is_present
        )
        SELECT
            m.id as meeting_id,
            m.company_id,
            (attendee->>'email')::text as email,
            (attendee->>'name')::text as name,
            COALESCE((attendee->>'role')::text, 'attendee') as role,
            (attendee->>'user_id')::text as user_id,
            (attendee->>'joined_at')::timestamptz as joined_at,
            (attendee->>'left_at')::timestamptz as left_at,
            CASE WHEN (attendee->>'joined_at') IS NOT NULL THEN true ELSE false END as is_present
        FROM meetings m,
             jsonb_array_elements(m.attendees) as attendee
        WHERE jsonb_array_length(m.attendees) > 0
    """)

    # Update participant_count based on migrated data
    op.execute("""
        UPDATE meetings
        SET participant_count = (
            SELECT COUNT(*) FROM meeting_attendees ma WHERE ma.meeting_id = meetings.id
        )
        WHERE EXISTS (SELECT 1 FROM meeting_attendees ma WHERE ma.meeting_id = meetings.id)
    """)

    # ============================================
    # 6. CLEANUP AND OPTIMIZATION
    # ============================================

    # Analyze tables for query planner
    op.execute("ANALYZE meetings")
    op.execute("ANALYZE transcripts")
    op.execute("ANALYZE action_items")
    op.execute("ANALYZE meeting_attendees")

    # Add comments for documentation
    op.execute("COMMENT ON TABLE meeting_attendees IS 'Normalized attendee information for meetings. Replaces JSONB attendees field.'")
    op.execute("COMMENT ON COLUMN meetings.attendees IS 'DEPRECATED: Use meeting_attendees table instead'")


def downgrade() -> None:
    """
    Rollback database optimizations
    """

    # Remove triggers
    op.execute("DROP TRIGGER IF EXISTS meeting_status_transition_trigger ON meetings")
    op.execute("DROP FUNCTION IF EXISTS check_meeting_status_transition()")

    # Remove partitions (data will be moved back to main table)
    op.execute("DROP TABLE IF EXISTS transcripts CASCADE")

    # Recreate transcripts table without partitioning
    op.execute("""
        CREATE TABLE transcripts (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            meeting_id UUID REFERENCES meetings(id) ON DELETE CASCADE,
            company_id VARCHAR REFERENCES companies(id) ON DELETE CASCADE,
            user_id VARCHAR REFERENCES users(id) ON DELETE SET NULL,
            text TEXT NOT NULL,
            speaker_id VARCHAR(100),
            speaker_name VARCHAR(255),
            speaker_email VARCHAR(255),
            start_time FLOAT NOT NULL,
            end_time FLOAT NOT NULL,
            duration FLOAT NOT NULL,
            timestamp TIMESTAMPTZ,
            confidence FLOAT,
            language VARCHAR(10) DEFAULT 'en',
            channel INTEGER,
            sequence_number INTEGER NOT NULL,
            words JSONB,
            is_edited BOOLEAN DEFAULT FALSE,
            original_text TEXT,
            edited_by VARCHAR,
            edited_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    # Migrate data back from partitions (if they exist)
    # This is complex and would need custom logic based on partition names

    # Remove new indexes
    indexes_to_drop = [
        'idx_meeting_attendees_meeting_email',
        'idx_meeting_attendees_user',
        'idx_meeting_attendees_company',
        'idx_meetings_company_status_created',
        'idx_meetings_company_platform',
        'idx_meetings_scheduled_range',
        'idx_meetings_creator_status',
        'idx_transcripts_meeting_time',
        'idx_transcripts_speaker',
        'idx_transcripts_company_created',
        'idx_transcripts_search',
        'idx_action_items_company_status',
        'idx_action_items_assigned_due',
        'idx_action_items_meeting_status',
        'idx_action_items_priority_status',
        'idx_user_sessions_user_created',
        'idx_user_sessions_expires'
    ]

    for idx in indexes_to_drop:
        op.execute(f"DROP INDEX IF EXISTS {idx}")

    # Drop meeting_attendees table
    op.drop_table('meeting_attendees')