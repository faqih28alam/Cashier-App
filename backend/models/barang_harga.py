from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from database import Base


class BarangHarga(Base):
    __tablename__ = "barang_harga"

    id      = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(50), ForeignKey("barang.barcode"), nullable=False, index=True)
    min_qty = Column(Numeric(15, 2), nullable=False)
    harga   = Column(Numeric(15, 2), nullable=False, default=0)

    barang = relationship("Barang", back_populates="harga_tiers")
