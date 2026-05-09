from datetime import date
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user, require_role
from models.keuangan import Keuangan
from models.user import User
from schemas.keuangan import KeuanganCreate, KeuanganOut

router = APIRouter()


@router.get("/", response_model=list[KeuanganOut])
def list_keuangan(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
    tgl_mulai: date = Query(default=None),
    tgl_selesai: date = Query(default=None),
):
    q = db.query(Keuangan)
    if tgl_mulai:
        q = q.filter(func.date(Keuangan.tanggal) >= tgl_mulai)
    if tgl_selesai:
        q = q.filter(func.date(Keuangan.tanggal) <= tgl_selesai)
    return q.order_by(Keuangan.tanggal.desc()).all()


@router.post("/", response_model=KeuanganOut)
def create_manual_entry(
    payload: KeuanganCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    entry = Keuangan(**payload.model_dump(), ref_type="manual")
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
