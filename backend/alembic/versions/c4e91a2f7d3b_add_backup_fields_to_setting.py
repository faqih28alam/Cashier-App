"""add backup fields to setting

Revision ID: c4e91a2f7d3b
Revises: 8795c6f8a552
Create Date: 2026-07-08 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'c4e91a2f7d3b'
down_revision: Union[str, None] = '8795c6f8a552'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('setting', sa.Column('backup_client_id', sa.String(length=100), nullable=True))
    op.add_column('setting', sa.Column('backup_token', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    op.drop_column('setting', 'backup_token')
    op.drop_column('setting', 'backup_client_id')
