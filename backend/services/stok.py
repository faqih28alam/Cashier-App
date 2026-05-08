from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.barang import Barang


def decrement(db: Session, barcode: str, qty: Decimal) -> None:
    barang = db.get(Barang, barcode)
    if barang:
        new_stok = Decimal(str(barang.stok)) - qty
        if new_stok < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Stok {barang.nama_barang} tidak mencukupi (tersisa {barang.stok})",
            )
        barang.stok = new_stok
        db.flush()


def increment(db: Session, barcode: str, qty: Decimal) -> None:
    barang = db.get(Barang, barcode)
    if barang:
        barang.stok = Decimal(str(barang.stok)) + qty
        db.flush()
