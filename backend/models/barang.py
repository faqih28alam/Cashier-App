from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from database import Base


class Barang(Base):
    __tablename__ = "barang"

    barcode          = Column(String(50), primary_key=True, index=True)
    nama_barang      = Column(String(150), nullable=False, index=True)
    id_kategori      = Column(Integer, ForeignKey("kategori.id"), nullable=True)
    sat              = Column(String(20), nullable=False, default="PCS")
    hpp              = Column(Numeric(15, 2), nullable=False, default=0)
    harga_1          = Column(Numeric(15, 2), nullable=False, default=0)
    harga_2          = Column(Numeric(15, 2), nullable=False, default=0)
    min_qty_harga_2  = Column(Integer, nullable=False, default=0)
    harga_3          = Column(Numeric(15, 2), nullable=False, default=0)
    min_qty_harga_3  = Column(Integer, nullable=False, default=0)
    stok             = Column(Numeric(15, 2), nullable=False, default=0)
    stok_minimum     = Column(Numeric(15, 2), nullable=False, default=0)

    kategori = relationship("Kategori")
