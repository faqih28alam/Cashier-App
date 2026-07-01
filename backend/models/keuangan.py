from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from database import Base


class Keuangan(Base):
    __tablename__ = "keuangan"

    id          = Column(Integer, primary_key=True, index=True)
    tanggal     = Column(DateTime, nullable=False, default=datetime.now)
    keterangan  = Column(String(255), nullable=False)
    debit       = Column(Numeric(15, 2), nullable=False, default=0)   # cash in
    kredit      = Column(Numeric(15, 2), nullable=False, default=0)   # cash out
    ref_type    = Column(String(20))   # transaksi | pembelian | manual
    ref_id      = Column(Integer)      # id of the source record
