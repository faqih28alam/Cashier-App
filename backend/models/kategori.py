from sqlalchemy import Column, Integer, String
from database import Base


class Kategori(Base):
    __tablename__ = "kategori"

    id            = Column(Integer, primary_key=True, index=True)
    kode_kategori = Column(String(20), unique=True, nullable=False)
    nama_kategori = Column(String(100), nullable=False)
