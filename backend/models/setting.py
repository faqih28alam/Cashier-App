from sqlalchemy import Column, Integer, String
from database import Base


class Setting(Base):
    __tablename__ = "setting"

    id              = Column(Integer, primary_key=True, default=1)
    nama_toko       = Column(String(100), nullable=False, default="Toko Saya")
    alamat          = Column(String(255))
    telepon         = Column(String(20))
    printer_port    = Column(String(50))          # e.g. COM3, /dev/usb/lp0
    printer_width   = Column(Integer, default=80) # 58 or 80 mm
    receipt_footer  = Column(String(255), default="Terima Kasih!")
    tax_rate        = Column(Integer, default=0)  # percentage, 0 = no tax
