"""Add updated_at column to user_sessions

Revision ID: 6c3b9e69ba47
Revises: 001_initial_schema
Create Date: 2026-02-17 09:24:59.688486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c3b9e69ba47'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('user_sessions', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    op.drop_column('user_sessions', 'updated_at')
