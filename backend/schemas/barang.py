from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class BarangHargaIn(BaseModel):
    min_qty: Decimal
    harga: Decimal


class BarangHargaOut(BarangHargaIn):
    id: int

    model_config = {"from_attributes": True}


class BarangCreate(BaseModel):
    barcode: str
    nama_barang: str
    id_kategori: Optional[int] = None
    sat: str = "PCS"
    hpp: Decimal = Decimal("0")
    harga_1: Decimal = Decimal("0")
    stok: Decimal = Decimal("0")
    stok_minimum: Decimal = Decimal("0")
    harga_tiers: list[BarangHargaIn] = []


class BarangUpdate(BaseModel):
    barcode: Optional[str] = None
    nama_barang: Optional[str] = None
    id_kategori: Optional[int] = None
    sat: Optional[str] = None
    hpp: Optional[Decimal] = None
    harga_1: Optional[Decimal] = None
    stok: Optional[Decimal] = None
    stok_minimum: Optional[Decimal] = None
    harga_tiers: Optional[list[BarangHargaIn]] = None


class BarangOut(BaseModel):
    barcode: str
    nama_barang: str
    id_kategori: Optional[int] = None
    sat: str
    hpp: Decimal
    harga_1: Decimal
    stok: Decimal
    stok_minimum: Decimal
    nama_kategori: Optional[str] = None
    harga_tiers: list[BarangHargaOut] = []

    model_config = {"from_attributes": True}
