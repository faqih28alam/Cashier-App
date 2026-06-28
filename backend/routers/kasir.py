from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user, require_role
from models.setting import Setting
from models.user import User
from models.transaksi import Transaksi
from schemas.transaksi import TransaksiCreate, TransaksiOut
from services import transaksi as transaksi_service
from printer import print_receipt

router = APIRouter()


@router.post("/transaksi", response_model=TransaksiOut)
def buat_transaksi(
    payload: TransaksiCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    trx = transaksi_service.create(db, payload, current_user.id)
    setting = db.get(Setting, 1)
    if setting is None or setting.auto_print is not False:
        try:
            print_receipt(db, trx)
        except Exception:
            pass  # transaction is saved; printer failure is non-fatal
    return trx


@router.get("/session")
def cek_session(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    held = (
        db.query(Transaksi)
        .filter(Transaksi.id_user == current_user.id, Transaksi.status == "open")
        .order_by(Transaksi.tanggal.desc())
        .first()
    )
    return {"has_held": held is not None, "transaksi": TransaksiOut.model_validate(held) if held else None}


@router.get("/transaksi/{id}", response_model=TransaksiOut)
def get_transaksi(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    trx = db.get(Transaksi, id)
    if not trx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    return trx


@router.post("/transaksi/{id}/void", response_model=TransaksiOut)
def void_transaksi(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    return transaksi_service.void(db, id)
