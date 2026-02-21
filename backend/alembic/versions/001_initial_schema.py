"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-02-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create all tables for Vocaply platform
    """
    
    # ============================================
    # EXTENSIONS
    # ============================================
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')  # For full-text search
    
    
    # ============================================
    # COMPANIES TABLE (Multi-tenant root)
    # ============================================
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), unique=True, nullable=False, index=True),
        
        # Subscription
        sa.Column('plan', sa.String(50), nullable=False, server_default='trial'),
        sa.Column('subscription_status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('trial_ends_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('subscription_started_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('subscription_current_period_start', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('subscription_current_period_end', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # Quotas
        sa.Column('meeting_quota_monthly', sa.Integer, nullable=False, server_default='25'),
        sa.Column('meetings_used_current_month', sa.Integer, nullable=False, server_default='0'),
        sa.Column('quota_reset_date', sa.Date, nullable=True),
        sa.Column('seat_count', sa.Integer, nullable=False, server_default='5'),
        sa.Column('max_users', sa.Integer, nullable=False, server_default='10'),
        
        # Settings
        sa.Column('settings', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'),
        sa.Column('logo_url', sa.Text, nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('company_size', sa.String(50), nullable=True),
        
        # Billing
        sa.Column('stripe_customer_id', sa.String(255), nullable=True, unique=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True, unique=True),
        
        # Metadata
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    
    # Indexes for companies
    op.create_index('idx_companies_plan', 'companies', ['plan'])
    op.create_index('idx_companies_active', 'companies', ['is_active'])
    
    
    # ============================================
    # USERS TABLE
    # ============================================
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Authentication
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('email_verified', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('email_verification_token', sa.String(255), nullable=True, unique=True),
        sa.Column('email_verification_sent_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('password_reset_token', sa.String(255), nullable=True, unique=True),
        sa.Column('password_reset_expires', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # Profile
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.Text, nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('job_title', sa.String(100), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        
        # Role & Permissions
        sa.Column('role', sa.String(50), nullable=False, server_default='member'),  # owner, admin, manager, member
        sa.Column('permissions', postgresql.JSONB, nullable=False, server_default='[]'),
        
        # Preferences
        sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'),
        sa.Column('language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('date_format', sa.String(20), nullable=False, server_default='MM/DD/YYYY'),
        sa.Column('time_format', sa.String(10), nullable=False, server_default='12h'),
        sa.Column('notification_preferences', postgresql.JSONB, nullable=False, server_default=sa.text("""
            '{
                "email": true,
                "slack": true,
                "in_app": true,
                "daily_digest": true,
                "reminders": true,
                "action_item_assigned": true,
                "action_item_completed": true,
                "meeting_starting_soon": true,
                "weekly_summary": true
            }'
        """)),
        
        # Bot Settings
        sa.Column('auto_join_meetings', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('auto_join_platforms', postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY['zoom','meet','teams']::varchar[]")),
        sa.Column('auto_join_only_if_organizer', sa.Boolean, nullable=False, server_default='false'),
        
        # Status
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('is_email_verified', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('last_login_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('last_seen_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('login_count', sa.Integer, nullable=False, server_default='0'),
        
        # Onboarding
        sa.Column('onboarding_completed', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('onboarding_step', sa.Integer, nullable=False, server_default='0'),
        
        # Metadata
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    
    # Indexes for users
    op.create_index('idx_users_company', 'users', ['company_id'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_active', 'users', ['is_active'])
    
    
    # ============================================
    # USER SESSIONS TABLE (Refresh Tokens)
    # ============================================
    op.create_table(
        'user_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('refresh_token', sa.String(500), nullable=False, unique=True, index=True),
        sa.Column('device_info', postgresql.JSONB, nullable=True),
        sa.Column('ip_address', postgresql.INET, nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_used_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    
    # Index for session cleanup
    op.create_index('idx_sessions_expires', 'user_sessions', ['expires_at'])
    
    
    # ============================================
    # MEETINGS TABLE
    # ============================================
    op.create_table(
        'meetings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        
        # Meeting Details
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('meeting_url', sa.Text, nullable=True),
        sa.Column('meeting_password', sa.String(100), nullable=True),
        
        # Platform
        sa.Column('platform', sa.String(50), nullable=True),  # zoom, meet, teams, other
        sa.Column('platform_meeting_id', sa.String(255), nullable=True, index=True),
        sa.Column('platform_join_url', sa.Text, nullable=True),
        sa.Column('platform_start_url', sa.Text, nullable=True),
        
        # Scheduling
        sa.Column('scheduled_start', sa.TIMESTAMP(timezone=True), nullable=True, index=True),
        sa.Column('scheduled_end', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('actual_start', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('actual_end', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer, nullable=True),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'),
        
        # Participants
        sa.Column('attendees', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('organizer_email', sa.String(255), nullable=True),
        sa.Column('participant_count', sa.Integer, nullable=False, server_default='0'),
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, server_default='scheduled'),  # scheduled, in_progress, transcribing, analyzing, completed, cancelled
        
        # Recording
        sa.Column('recording_url', sa.Text, nullable=True),
        sa.Column('recording_s3_key', sa.Text, nullable=True),
        sa.Column('recording_size_bytes', sa.BigInteger, nullable=True),
        sa.Column('recording_duration_seconds', sa.Integer, nullable=True),
        
        # Bot
        sa.Column('bot_instance_id', sa.String(255), nullable=True),
        sa.Column('bot_status', sa.String(50), nullable=True),  # joining, in_call, left, failed
        sa.Column('bot_joined_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('bot_left_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('bot_enabled', sa.Boolean, nullable=False, server_default='false'),
        
        # Transcription
        sa.Column('transcript_status', sa.String(50), nullable=True),  # pending, processing, completed, failed
        sa.Column('transcript_completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('transcript_word_count', sa.Integer, nullable=True),
        
        # AI Analysis
        sa.Column('ai_analysis_status', sa.String(50), nullable=True),  # pending, processing, completed, failed
        sa.Column('ai_analysis_completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('action_items_count', sa.Integer, nullable=False, server_default='0'),
        
        # Metadata
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY[]::varchar[]")),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('notes', sa.Text, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    
    # Indexes for meetings
    op.create_index('idx_meetings_company', 'meetings', ['company_id'])
    op.create_index('idx_meetings_status', 'meetings', ['status'])
    op.create_index('idx_meetings_scheduled', 'meetings', ['scheduled_start'])
    op.create_index('idx_meetings_platform', 'meetings', ['platform'])
    op.create_index('idx_meetings_created_by', 'meetings', ['created_by'])
    
    
    # ============================================
    # TRANSCRIPTS TABLE
    # ============================================
    op.create_table(
        'transcripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Transcript Content
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('speaker_id', sa.String(100), nullable=True),
        sa.Column('speaker_name', sa.String(255), nullable=True),
        sa.Column('speaker_email', sa.String(255), nullable=True, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        
        # Timing
        sa.Column('start_time', sa.Float, nullable=False),  # Seconds from meeting start
        sa.Column('end_time', sa.Float, nullable=False),
        sa.Column('duration', sa.Float, nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # Metadata
        sa.Column('confidence', sa.Float, nullable=True),  # 0.0 to 1.0
        sa.Column('words', postgresql.JSONB, nullable=True),  # Word-level timestamps
        sa.Column('channel', sa.Integer, nullable=True),
        sa.Column('language', sa.String(10), nullable=False, server_default='en'),
        
        # Sequence
        sa.Column('sequence_number', sa.Integer, nullable=False),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Indexes for transcripts
    op.create_index('idx_transcripts_meeting', 'transcripts', ['meeting_id'])
    op.create_index('idx_transcripts_speaker', 'transcripts', ['speaker_email'])
    op.create_index('idx_transcripts_sequence', 'transcripts', ['meeting_id', 'sequence_number'])
    
    # Full-text search index
    op.execute("""
        CREATE INDEX idx_transcripts_text_search 
        ON transcripts 
        USING gin(to_tsvector('english', text))
    """)
    
    
    # ============================================
    # ACTION ITEMS TABLE
    # ============================================
    op.create_table(
        'action_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        
        # Task Details
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        
        # Assignment
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('assigned_email', sa.String(255), nullable=True),  # From AI extraction
        sa.Column('assigned_name', sa.String(255), nullable=True),
        
        # Status & Priority
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),  # pending, in_progress, completed, cancelled
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium'),  # urgent, high, medium, low
        
        # Dates
        sa.Column('due_date', sa.TIMESTAMP(timezone=True), nullable=True, index=True),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # AI Extraction Data
        sa.Column('extracted_by_ai', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('ai_confidence', sa.Float, nullable=True),  # 0.0 to 1.0
        sa.Column('transcript_quote', sa.Text, nullable=True),  # Original quote from meeting
        sa.Column('transcript_timestamp', sa.Float, nullable=True),  # Timestamp in meeting
        sa.Column('ai_extraction_metadata', postgresql.JSONB, nullable=True),
        
        # Integration Sync
        sa.Column('integration_task_id', sa.String(255), nullable=True),  # External system ID (Asana, Jira, etc)
        sa.Column('integration_type', sa.String(50), nullable=True),  # asana, jira, linear, slack
        sa.Column('integration_url', sa.Text, nullable=True),
        sa.Column('synced_at', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # Metadata
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY[]::varchar[]")),
        sa.Column('attachments', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    
    # Indexes for action items
    op.create_index('idx_action_items_meeting', 'action_items', ['meeting_id'])
    op.create_index('idx_action_items_company', 'action_items', ['company_id'])
    op.create_index('idx_action_items_assigned', 'action_items', ['assigned_to'])
    op.create_index('idx_action_items_status', 'action_items', ['status'])
    op.create_index('idx_action_items_priority', 'action_items', ['priority'])
    op.create_index('idx_action_items_due', 'action_items', ['due_date'])
    op.create_index('idx_action_items_status_assigned', 'action_items', ['status', 'assigned_to'])
    
    
    # ============================================
    # MEETING SUMMARIES TABLE
    # ============================================
    op.create_table(
        'meeting_summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Summary Content
        sa.Column('overview', sa.Text, nullable=True),
        sa.Column('key_points', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('decisions_made', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('topics_discussed', postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY[]::varchar[]")),
        sa.Column('next_steps', postgresql.JSONB, nullable=False, server_default='[]'),
        
        # Sentiment Analysis
        sa.Column('overall_sentiment', sa.String(20), nullable=True),  # positive, neutral, negative
        sa.Column('sentiment_score', sa.Float, nullable=True),  # -1.0 to 1.0
        
        # AI Metadata
        sa.Column('generated_by', sa.String(50), nullable=False, server_default='ai'),
        sa.Column('ai_model', sa.String(100), nullable=True),
        sa.Column('ai_confidence', sa.Float, nullable=True),
        sa.Column('tokens_used', sa.Integer, nullable=True),
        sa.Column('generation_cost', sa.Numeric(10, 6), nullable=True),
        
        # Version Control
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
        sa.Column('is_edited', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('edited_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('edited_at', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Index for summaries
    op.create_index('idx_summaries_meeting', 'meeting_summaries', ['meeting_id'])
    
    
    # ============================================
    # NOTIFICATIONS TABLE
    # ============================================
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Notification Content
        sa.Column('type', sa.String(100), nullable=False),  # action_item_assigned, meeting_starting, etc
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('action_url', sa.Text, nullable=True),
        sa.Column('action_text', sa.String(100), nullable=True),
        
        # Channel
        sa.Column('channel', sa.String(50), nullable=False),  # in_app, email, slack, push
        
        # Related Entities
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=True),
        sa.Column('action_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('action_items.id', ondelete='CASCADE'), nullable=True),
        
        # Status
        sa.Column('is_read', sa.Boolean, nullable=False, server_default='false', index=True),
        sa.Column('read_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('sent_at', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Indexes for notifications
    op.create_index('idx_notifications_user', 'notifications', ['user_id'])
    op.create_index('idx_notifications_unread', 'notifications', ['user_id', 'is_read'])
    op.create_index('idx_notifications_created', 'notifications', ['created_at'])
    
    
    # ============================================
    # INTEGRATIONS TABLE
    # ============================================
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Integration Type
        sa.Column('integration_type', sa.String(50), nullable=False),  # slack, asana, jira, linear, zoom, meet, teams
        sa.Column('integration_name', sa.String(255), nullable=False),
        
        # OAuth Tokens
        sa.Column('access_token', sa.Text, nullable=True),
        sa.Column('refresh_token', sa.Text, nullable=True),
        sa.Column('token_expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('token_type', sa.String(50), nullable=True),
        sa.Column('scope', sa.Text, nullable=True),
        
        # Platform-specific IDs
        sa.Column('external_user_id', sa.String(255), nullable=True),
        sa.Column('external_workspace_id', sa.String(255), nullable=True),
        sa.Column('external_team_id', sa.String(255), nullable=True),
        
        # Configuration
        sa.Column('config', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('preferences', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Status
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true', index=True),
        sa.Column('last_synced_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('sync_status', sa.String(50), nullable=True),  # success, failed, in_progress
        sa.Column('sync_error', sa.Text, nullable=True),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Indexes for integrations
    op.create_index('idx_integrations_company', 'integrations', ['company_id'])
    op.create_index('idx_integrations_user', 'integrations', ['user_id'])
    op.create_index('idx_integrations_type', 'integrations', ['integration_type'])
    op.create_index('idx_integrations_active', 'integrations', ['is_active'])
    
    # Unique constraint: one integration type per company
    op.create_index('idx_integrations_company_type', 'integrations', ['company_id', 'integration_type'], unique=True)
    
    
    # ============================================
    # PLATFORM CONNECTIONS TABLE
    # ============================================
    op.create_table(
        'platform_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Platform
        sa.Column('platform', sa.String(50), nullable=False),  # zoom, google_meet, teams
        
        # OAuth Tokens
        sa.Column('access_token', sa.Text, nullable=True),
        sa.Column('refresh_token', sa.Text, nullable=True),
        sa.Column('token_expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # Platform-specific IDs
        sa.Column('platform_user_id', sa.String(255), nullable=True),
        sa.Column('platform_user_email', sa.String(255), nullable=True),
        
        # Configuration
        sa.Column('config', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Status
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('last_synced_at', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Indexes for platform connections
    op.create_index('idx_platform_connections_company', 'platform_connections', ['company_id'])
    op.create_index('idx_platform_connections_user', 'platform_connections', ['user_id'])
    op.create_index('idx_platform_connections_platform', 'platform_connections', ['platform'])
    
    # Unique constraint
    op.create_index('idx_platform_connections_unique', 'platform_connections', ['company_id', 'platform'], unique=True)
    
    
    # ============================================
    # BOT SESSIONS TABLE
    # ============================================
    op.create_table(
        'bot_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Bot Instance
        sa.Column('bot_instance_id', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('platform', sa.String(50), nullable=False),  # zoom, meet, teams
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, server_default='initializing'),  # initializing, joining, in_call, leaving, left, error
        sa.Column('error_message', sa.Text, nullable=True),
        
        # Timing
        sa.Column('joined_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('left_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer, nullable=True),
        
        # Recording
        sa.Column('recording_started_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('recording_stopped_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('recording_url', sa.Text, nullable=True),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Indexes for bot sessions
    op.create_index('idx_bot_sessions_meeting', 'bot_sessions', ['meeting_id'])
    op.create_index('idx_bot_sessions_status', 'bot_sessions', ['status'])
    
    
    # ============================================
    # CALENDAR EVENTS TABLE
    # ============================================
    op.create_table(
        'calendar_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Calendar Provider
        sa.Column('calendar_provider', sa.String(50), nullable=False),  # google, outlook
        sa.Column('event_id', sa.String(255), nullable=False),
        
        # Event Details
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('start_time', sa.TIMESTAMP(timezone=True), nullable=False, index=True),
        sa.Column('end_time', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('timezone', sa.String(50), nullable=False),
        sa.Column('location', sa.String(500), nullable=True),
        
        # Meeting Detection
        sa.Column('meeting_platform', sa.String(50), nullable=True),  # zoom, meet, teams
        sa.Column('meeting_url', sa.Text, nullable=True),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id', ondelete='SET NULL'), nullable=True, index=True),
        
        # Auto-join
        sa.Column('auto_join_enabled', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('bot_scheduled', sa.Boolean, nullable=False, server_default='false'),
        
        # Sync Status
        sa.Column('synced_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Indexes for calendar events
    op.create_index('idx_calendar_events_user', 'calendar_events', ['user_id'])
    op.create_index('idx_calendar_events_start', 'calendar_events', ['start_time'])
    op.create_index('idx_calendar_events_auto_join', 'calendar_events', ['auto_join_enabled', 'start_time'])
    
    # Unique constraint
    op.create_index('idx_calendar_events_unique', 'calendar_events', ['user_id', 'event_id'], unique=True)
    
    
    # ============================================
    # SUBSCRIPTIONS TABLE
    # ============================================
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        
        # Stripe
        sa.Column('stripe_customer_id', sa.String(255), nullable=True, unique=True, index=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True, unique=True, index=True),
        sa.Column('stripe_price_id', sa.String(255), nullable=True),
        sa.Column('stripe_product_id', sa.String(255), nullable=True),
        
        # Subscription Details
        sa.Column('plan_name', sa.String(50), nullable=False),  # starter, professional, enterprise
        sa.Column('billing_interval', sa.String(20), nullable=False),  # monthly, yearly
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='usd'),
        
        # Status
        sa.Column('status', sa.String(50), nullable=False),  # active, trialing, past_due, canceled, incomplete
        sa.Column('cancel_at_period_end', sa.Boolean, nullable=False, server_default='false'),
        
        # Periods
        sa.Column('current_period_start', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('trial_start', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('trial_end', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('canceled_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('ended_at', sa.TIMESTAMP(timezone=True), nullable=True),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    
    # ============================================
    # AI USAGE TABLE
    # ============================================
    op.create_table(
        'ai_usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('meetings.id', ondelete='CASCADE'), nullable=True, index=True),
        
        # AI Provider
        sa.Column('provider', sa.String(50), nullable=False),  # openai, deepgram
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('operation', sa.String(100), nullable=False),  # transcription, extraction, summary
        
        # Usage
        sa.Column('input_tokens', sa.Integer, nullable=True),
        sa.Column('output_tokens', sa.Integer, nullable=True),
        sa.Column('total_tokens', sa.Integer, nullable=True),
        sa.Column('duration_seconds', sa.Float, nullable=True),
        
        # Cost
        sa.Column('cost_usd', sa.Numeric(10, 6), nullable=True),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Timestamp
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Indexes for AI usage
    op.create_index('idx_ai_usage_company', 'ai_usage', ['company_id'])
    op.create_index('idx_ai_usage_meeting', 'ai_usage', ['meeting_id'])
    op.create_index('idx_ai_usage_date', 'ai_usage', ['created_at'])
    
    
    # ============================================
    # AUDIT LOG TABLE
    # ============================================
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        
        # Action
        sa.Column('action', sa.String(100), nullable=False),  # create, update, delete
        sa.Column('entity_type', sa.String(100), nullable=False),  # meeting, action_item, user
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        
        # Details
        sa.Column('changes', postgresql.JSONB, nullable=True),
        sa.Column('ip_address', postgresql.INET, nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Timestamp
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Indexes for audit logs
    op.create_index('idx_audit_logs_company', 'audit_logs', ['company_id'])
    op.create_index('idx_audit_logs_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_logs_created', 'audit_logs', ['created_at'])
    
    
    # ============================================
    # TRIGGERS FOR UPDATED_AT
    # ============================================
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Apply trigger to all tables with updated_at
    tables_with_updated_at = [
        'companies', 'users', 'meetings', 'transcripts', 'action_items',
        'meeting_summaries', 'integrations', 'platform_connections',
        'bot_sessions', 'calendar_events', 'subscriptions'
    ]
    
    for table in tables_with_updated_at:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    """
    Drop all tables in reverse order
    """
    # Drop triggers first
    tables_with_updated_at = [
        'companies', 'users', 'meetings', 'transcripts', 'action_items',
        'meeting_summaries', 'integrations', 'platform_connections',
        'bot_sessions', 'calendar_events', 'subscriptions'
    ]
    
    for table in tables_with_updated_at:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    
    # Drop tables in reverse order of creation
    op.drop_table('audit_logs')
    op.drop_table('ai_usage')
    op.drop_table('subscriptions')
    op.drop_table('calendar_events')
    op.drop_table('bot_sessions')
    op.drop_table('platform_connections')
    op.drop_table('integrations')
    op.drop_table('notifications')
    op.drop_table('meeting_summaries')
    op.drop_table('action_items')
    op.drop_table('transcripts')
    op.drop_table('meetings')
    op.drop_table('user_sessions')
    op.drop_table('users')
    op.drop_table('companies')
    
    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')