from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship
from database import Base


class Transaksi(Base):
    __tablename__ = "transaksi"

    id             = Column(Integer, primary_key=True, index=True)
    no_transaksi   = Column(String(30), unique=True, nullable=False, index=True)
    tanggal        = Column(DateTime, nullable=False, default=func.now())
    id_user        = Column(Integer, ForeignKey("user.id"), nullable=False)
    total          = Column(Numeric(15, 2), nullable=False, default=0)
    bayar          = Column(Numeric(15, 2), nullable=False, default=0)
    kembalian      = Column(Numeric(15, 2), nullable=False, default=0)
    status         = Column(String(20), nullable=False, default="open")  # open | paid | cancelled

    user   = relationship("User")
    detail = relationship("TransaksiDetail", back_populates="transaksi", cascade="all, delete-orphan")


class TransaksiDetail(Base):
    __tablename__ = "transaksi_detail"

    id           = Column(Integer, primary_key=True, index=True)
    id_transaksi = Column(Integer, ForeignKey("transaksi.id"), nullable=False)
    barcode      = Column(String(50), nullable=False)
    nama_barang  = Column(String(150), nullable=False)
    sat          = Column(String(20), nullable=False)
    qty          = Column(Numeric(15, 2), nullable=False)
    hpp          = Column(Numeric(15, 2), nullable=False, default=0)
    harga        = Column(Numeric(15, 2), nullable=False)
    diskon       = Column(Numeric(15, 2), nullable=False, default=0)
    total        = Column(Numeric(15, 2), nullable=False)

    transaksi = relationship("Transaksi", back_populates="detail")
