from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship
from database import Base


class Pembelian(Base):
    __tablename__ = "pembelian"

    id          = Column(Integer, primary_key=True, index=True)
    no_faktur   = Column(String(50), unique=True, nullable=False, index=True)
    tanggal     = Column(DateTime, nullable=False, default=func.now())
    id_supplier = Column(Integer, ForeignKey("supplier.id"), nullable=True)
    total       = Column(Numeric(15, 2), nullable=False, default=0)
    status      = Column(String(20), nullable=False, default="draft")  # draft | confirmed

    supplier = relationship("Supplier")
    detail   = relationship("PembelianDetail", back_populates="pembelian", cascade="all, delete-orphan")


class PembelianDetail(Base):
    __tablename__ = "pembelian_detail"

    id           = Column(Integer, primary_key=True, index=True)
    id_pembelian = Column(Integer, ForeignKey("pembelian.id"), nullable=False)
    barcode      = Column(String(50), ForeignKey("barang.barcode"), nullable=False)
    nama_barang  = Column(String(150), nullable=False)
    sat          = Column(String(20), nullable=False)
    qty          = Column(Numeric(15, 2), nullable=False)
    hpp          = Column(Numeric(15, 2), nullable=False, default=0)
    total        = Column(Numeric(15, 2), nullable=False)

    pembelian = relationship("Pembelian", back_populates="detail")
    barang    = relationship("Barang")
