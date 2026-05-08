from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class TransaksiDetailIn(BaseModel):
    barcode: str
    nama_barang: str
    sat: str
    qty: Decimal
    hpp: Decimal
    harga: Decimal
    diskon: Decimal = Decimal("0")


class TransaksiCreate(BaseModel):
    bayar: Decimal
    detail: list[TransaksiDetailIn]


class TransaksiDetailOut(TransaksiDetailIn):
    id: int
    total: Decimal

    model_config = {"from_attributes": True}


class TransaksiOut(BaseModel):
    id: int
    no_transaksi: str
    tanggal: datetime
    id_user: int
    total: Decimal
    bayar: Decimal
    kembalian: Decimal
    status: str
    detail: list[TransaksiDetailOut] = []

    model_config = {"from_attributes": True}
