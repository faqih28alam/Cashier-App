from typing import Optional
from pydantic import BaseModel


class SettingUpdate(BaseModel):
    nama_toko: Optional[str] = None
    alamat: Optional[str] = None
    telepon: Optional[str] = None
    printer_port: Optional[str] = None
    printer_width: Optional[int] = None
    receipt_footer: Optional[str] = None
    tax_rate: Optional[int] = None
    auto_print: Optional[bool] = None


class SettingOut(SettingUpdate):
    id: int

    model_config = {"from_attributes": True}
