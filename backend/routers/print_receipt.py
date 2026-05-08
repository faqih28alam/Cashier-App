from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user
from models.transaksi import Transaksi
from models.user import User
from printer import print_receipt

router = APIRouter()


@router.post("/receipt/{transaksi_id}")
def reprint(
    transaksi_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    trx = db.get(Transaksi, transaksi_id)
    if not trx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    try:
        print_receipt(db, trx)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Printer error: {str(e)}")
    return {"status": "printed"}
