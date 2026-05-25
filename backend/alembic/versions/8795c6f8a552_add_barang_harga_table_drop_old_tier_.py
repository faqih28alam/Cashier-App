"""add barang_harga table, drop old tier columns

Revision ID: 8795c6f8a552
Revises: 71bdcc288bd8
Create Date: 2026-05-25 20:36:15.228863

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '8795c6f8a552'
down_revision: Union[str, None] = '71bdcc288bd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('barang_harga',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('barcode', sa.String(length=50), nullable=False),
        sa.Column('min_qty', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('harga', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['barcode'], ['barang.barcode'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_barang_harga_barcode'), 'barang_harga', ['barcode'], unique=False)
    op.create_index(op.f('ix_barang_harga_id'), 'barang_harga', ['id'], unique=False)

    # Migrate existing tier data before dropping columns
    conn = op.get_bind()
    rows = conn.execute(sa.text(
        "SELECT barcode, harga_2, min_qty_harga_2, harga_3, min_qty_harga_3 FROM barang"
    )).fetchall()
    for row in rows:
        if row[2] and int(row[2]) > 0:
            conn.execute(sa.text(
                "INSERT INTO barang_harga (barcode, min_qty, harga) VALUES (:b, :m, :h)"
            ), {"b": row[0], "m": row[2], "h": row[1]})
        if row[4] and int(row[4]) > 0:
            conn.execute(sa.text(
                "INSERT INTO barang_harga (barcode, min_qty, harga) VALUES (:b, :m, :h)"
            ), {"b": row[0], "m": row[4], "h": row[3]})

    with op.batch_alter_table('barang') as batch:
        batch.drop_column('harga_2')
        batch.drop_column('min_qty_harga_2')
        batch.drop_column('harga_3')
        batch.drop_column('min_qty_harga_3')


def downgrade() -> None:
    with op.batch_alter_table('barang') as batch:
        batch.add_column(sa.Column('harga_3', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'))
        batch.add_column(sa.Column('min_qty_harga_2', sa.Integer(), nullable=False, server_default='0'))
        batch.add_column(sa.Column('min_qty_harga_3', sa.Integer(), nullable=False, server_default='0'))
        batch.add_column(sa.Column('harga_2', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'))

    op.drop_index(op.f('ix_barang_harga_id'), table_name='barang_harga')
    op.drop_index(op.f('ix_barang_harga_barcode'), table_name='barang_harga')
    op.drop_table('barang_harga')
