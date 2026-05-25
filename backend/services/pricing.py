from decimal import Decimal
from models.barang import Barang


def resolve_price(barang: Barang, qty: Decimal) -> Decimal:
    tiers = sorted(barang.harga_tiers, key=lambda t: t.min_qty, reverse=True)
    for tier in tiers:
        if qty >= tier.min_qty:
            return Decimal(str(tier.harga))
    return Decimal(str(barang.harga_1))
