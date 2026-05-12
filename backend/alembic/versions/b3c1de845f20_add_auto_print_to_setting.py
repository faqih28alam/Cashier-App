"""add auto_print to setting

Revision ID: b3c1de845f20
Revises: a7b2bc743e59
Create Date: 2026-05-12 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b3c1de845f20'
down_revision: Union[str, None] = 'a7b2bc743e59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('setting', sa.Column('auto_print', sa.Boolean(), nullable=True, server_default=sa.true()))
    op.execute("UPDATE setting SET auto_print = 1 WHERE auto_print IS NULL")


def downgrade() -> None:
    op.drop_column('setting', 'auto_print')
