from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class BarangCreate(BaseModel):
    barcode: str
    nama_barang: str
    id_kategori: Optional[int] = None
    sat: str = "PCS"
    hpp: Decimal = Decimal("0")
    harga_1: Decimal = Decimal("0")
    harga_2: Decimal = Decimal("0")
    min_qty_harga_2: int = 0
    harga_3: Decimal = Decimal("0")
    min_qty_harga_3: int = 0
    stok: Decimal = Decimal("0")
    stok_minimum: Decimal = Decimal("0")


class BarangUpdate(BarangCreate):
    barcode: Optional[str] = None


class BarangOut(BarangCreate):
    nama_kategori: Optional[str] = None

    model_config = {"from_attributes": True}
