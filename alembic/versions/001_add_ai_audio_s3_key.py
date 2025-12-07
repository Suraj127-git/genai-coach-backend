"""Add ai_audio_s3_key to ai_interview_interactions

Revision ID: 001
Revises:
Create Date: 2025-01-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add ai_audio_s3_key column to ai_interview_interactions table
    op.add_column('ai_interview_interactions',
                  sa.Column('ai_audio_s3_key', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove ai_audio_s3_key column from ai_interview_interactions table
    op.drop_column('ai_interview_interactions', 'ai_audio_s3_key')
