from datetime import date
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from dependencies import get_db, require_role
from models.user import User
from schemas.barang import BarangOut
from services import laporan as laporan_service

router = APIRouter()


@router.get("/penjualan")
def penjualan_harian(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
    tgl_mulai: date = Query(...),
    tgl_selesai: date = Query(...),
):
    return laporan_service.penjualan_harian(db, tgl_mulai, tgl_selesai)


@router.get("/produk-terlaris")
def produk_terlaris(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
    tgl_mulai: date = Query(...),
    tgl_selesai: date = Query(...),
    limit: int = Query(default=10),
):
    return laporan_service.produk_terlaris(db, tgl_mulai, tgl_selesai, limit)


@router.get("/stok", response_model=list[BarangOut])
def laporan_stok(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    return laporan_service.stok_list(db)


@router.get("/transaksi")
def riwayat_transaksi(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
    tgl_mulai: date = Query(...),
    tgl_selesai: date = Query(...),
):
    return laporan_service.transaksi_list(db, tgl_mulai, tgl_selesai)
