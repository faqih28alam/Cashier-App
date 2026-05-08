from decimal import Decimal
from models.barang import Barang


def resolve_price(barang: Barang, qty: Decimal) -> Decimal:
    """Return the correct price tier based on quantity."""
    if barang.min_qty_harga_3 > 0 and qty >= barang.min_qty_harga_3:
        return Decimal(str(barang.harga_3))
    if barang.min_qty_harga_2 > 0 and qty >= barang.min_qty_harga_2:
        return Decimal(str(barang.harga_2))
    return Decimal(str(barang.harga_1))
