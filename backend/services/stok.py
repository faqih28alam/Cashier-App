from decimal import Decimal
from sqlalchemy.orm import Session
from models.barang import Barang


def decrement(db: Session, barcode: str, qty: Decimal) -> None:
    barang = db.get(Barang, barcode)
    if barang:
        barang.stok = Decimal(str(barang.stok)) - qty
        db.flush()


def increment(db: Session, barcode: str, qty: Decimal) -> None:
    barang = db.get(Barang, barcode)
    if barang:
        barang.stok = Decimal(str(barang.stok)) + qty
        db.flush()
