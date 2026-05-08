from sqlalchemy import Column, Integer, String
from database import Base


class Supplier(Base):
    __tablename__ = "supplier"

    id            = Column(Integer, primary_key=True, index=True)
    kode_supplier = Column(String(20), unique=True, nullable=False)
    nama_supplier = Column(String(100), nullable=False)
    alamat        = Column(String(255))
    telepon       = Column(String(20))
    kontak        = Column(String(100))
