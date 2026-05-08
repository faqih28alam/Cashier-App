from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class PembelianDetailIn(BaseModel):
    barcode: str
    nama_barang: str
    sat: str
    qty: Decimal
    hpp: Decimal


class PembelianCreate(BaseModel):
    no_faktur: str
    tanggal: datetime
    id_supplier: Optional[int] = None
    detail: list[PembelianDetailIn]


class PembelianDetailOut(PembelianDetailIn):
    id: int
    total: Decimal

    model_config = {"from_attributes": True}


class PembelianOut(BaseModel):
    id: int
    no_faktur: str
    tanggal: datetime
    id_supplier: Optional[int]
    total: Decimal
    status: str
    detail: list[PembelianDetailOut] = []

    model_config = {"from_attributes": True}
