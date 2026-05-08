from typing import Optional
from pydantic import BaseModel


class KategoriCreate(BaseModel):
    kode_kategori: str
    nama_kategori: str


class KategoriOut(KategoriCreate):
    id: int

    model_config = {"from_attributes": True}


class SupplierCreate(BaseModel):
    kode_supplier: str
    nama_supplier: str
    alamat: Optional[str] = None
    telepon: Optional[str] = None
    kontak: Optional[str] = None


class SupplierOut(SupplierCreate):
    id: int

    model_config = {"from_attributes": True}
