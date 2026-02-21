"""Create ai_usage table

Revision ID: a1b2c3d4e5f6
Revises: 94d6d2b58c6a
Create Date: 2026-02-19 21:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '94d6d2b58c6a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ai_usage',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=False),
            server_default=sa.text('uuid_generate_v4()'),
            nullable=False,
        ),
        # Foreign keys
        sa.Column('company_id',  sa.String(),               nullable=False),
        sa.Column('meeting_id',  postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('user_id',     sa.String(),               nullable=True),

        # Request details
        sa.Column('feature_type',   sa.String(length=100),  nullable=False),
        sa.Column('model',          sa.String(length=100),  nullable=False,
                  server_default='gpt-4o-mini'),
        sa.Column('prompt_version', sa.String(length=50),   nullable=True),
        sa.Column('request_id',     sa.String(length=255),  nullable=True),
        sa.Column('status',         sa.String(length=50),   nullable=False,
                  server_default='success'),

        # Token usage
        sa.Column('prompt_tokens',     sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completion_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens',      sa.Integer(), nullable=False, server_default='0'),

        # Cost (stored as NUMERIC(12,8) for precision)
        sa.Column('prompt_cost',     sa.Numeric(12, 8), nullable=False, server_default='0'),
        sa.Column('completion_cost', sa.Numeric(12, 8), nullable=False, server_default='0'),
        sa.Column('total_cost',      sa.Numeric(12, 8), nullable=False, server_default='0'),

        # Performance
        sa.Column('latency_ms',   sa.Integer(), nullable=True),
        sa.Column('was_cached',   sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('retry_count',  sa.Integer(), nullable=False, server_default='0'),

        # Metadata / errors
        sa.Column(
            'metadata',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column('error_message', sa.Text(), nullable=True),

        # Date index field
        sa.Column(
            'usage_date',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),

        # Standard timestamps
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),

        # Constraints
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'],  ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'],    ['users.id'],     ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_id', name='uq_ai_usage_request_id'),
    )

    # Composite indexes for common query patterns
    op.create_index('idx_ai_usage_company_date',    'ai_usage', ['company_id', 'usage_date'],   unique=False)
    op.create_index('idx_ai_usage_company_feature', 'ai_usage', ['company_id', 'feature_type'], unique=False)
    op.create_index('idx_ai_usage_meeting',         'ai_usage', ['meeting_id'],                 unique=False)
    op.create_index('idx_ai_usage_status',          'ai_usage', ['status'],                     unique=False)

    # Standard single-column indexes
    op.create_index(op.f('ix_ai_usage_company_id'),  'ai_usage', ['company_id'],  unique=False)
    op.create_index(op.f('ix_ai_usage_meeting_id'),  'ai_usage', ['meeting_id'],  unique=False)
    op.create_index(op.f('ix_ai_usage_feature_type'),'ai_usage', ['feature_type'],unique=False)
    op.create_index(op.f('ix_ai_usage_usage_date'),  'ai_usage', ['usage_date'],  unique=False)
    op.create_index(op.f('ix_ai_usage_status'),      'ai_usage', ['status'],      unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ai_usage_status'),       table_name='ai_usage')
    op.drop_index(op.f('ix_ai_usage_usage_date'),   table_name='ai_usage')
    op.drop_index(op.f('ix_ai_usage_feature_type'), table_name='ai_usage')
    op.drop_index(op.f('ix_ai_usage_meeting_id'),   table_name='ai_usage')
    op.drop_index(op.f('ix_ai_usage_company_id'),   table_name='ai_usage')
    op.drop_index('idx_ai_usage_status',            table_name='ai_usage')
    op.drop_index('idx_ai_usage_meeting',           table_name='ai_usage')
    op.drop_index('idx_ai_usage_company_feature',   table_name='ai_usage')
    op.drop_index('idx_ai_usage_company_date',      table_name='ai_usage')
    op.drop_table('ai_usage')
