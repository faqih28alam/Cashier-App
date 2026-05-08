from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class KeuanganCreate(BaseModel):
    keterangan: str
    debit: Decimal = Decimal("0")
    kredit: Decimal = Decimal("0")


class KeuanganOut(KeuanganCreate):
    id: int
    tanggal: datetime
    ref_type: Optional[str]
    ref_id: Optional[int]

    model_config = {"from_attributes": True}
