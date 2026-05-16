from datetime import date
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user, require_role
from models.pembelian import Pembelian, PembelianDetail
from models.keuangan import Keuangan
from models.user import User
from schemas.pembelian import PembelianCreate, PembelianOut
from services import stok

router = APIRouter()


@router.get("/", response_model=list[PembelianOut])
def list_pembelian(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    tgl_mulai: date = Query(default=None),
    tgl_selesai: date = Query(default=None),
):
    q = db.query(Pembelian)
    if tgl_mulai:
        q = q.filter(func.date(Pembelian.tanggal) >= tgl_mulai)
    if tgl_selesai:
        q = q.filter(func.date(Pembelian.tanggal) <= tgl_selesai)
    return q.order_by(Pembelian.tanggal.desc()).all()


@router.post("/", response_model=PembelianOut)
def create_pembelian(
    payload: PembelianCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    total = sum(item.qty * item.hpp for item in payload.detail)
    pembelian = Pembelian(
        no_faktur=payload.no_faktur,
        tanggal=payload.tanggal,
        id_supplier=payload.id_supplier,
        total=total,
        status="draft",
    )
    db.add(pembelian)
    db.flush()

    for item in payload.detail:
        db.add(PembelianDetail(
            id_pembelian=pembelian.id,
            barcode=item.barcode,
            nama_barang=item.nama_barang,
            sat=item.sat,
            qty=item.qty,
            hpp=item.hpp,
            total=item.qty * item.hpp,
        ))

    db.commit()
    db.refresh(pembelian)
    return pembelian


@router.post("/{id}/confirm", response_model=PembelianOut)
def confirm_pembelian(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    pembelian = db.get(Pembelian, id)
    if not pembelian:
        raise HTTPException(status_code=404, detail="Pembelian tidak ditemukan")
    if pembelian.status == "confirmed":
        raise HTTPException(status_code=400, detail="Pembelian sudah dikonfirmasi")

    from models.barang import Barang
    auto_created = []
    for item in pembelian.detail:
        if not db.get(Barang, item.barcode):
            db.add(Barang(
                barcode=item.barcode,
                nama_barang=item.nama_barang,
                sat=item.sat,
                hpp=item.hpp,
                harga_1=0,
            ))
            db.flush()
            auto_created.append(item.nama_barang)
        stok.increment(db, item.barcode, item.qty)

    db.add(Keuangan(
        keterangan=f"Pembelian {pembelian.no_faktur}",
        debit=0,
        kredit=pembelian.total,
        ref_type="pembelian",
        ref_id=pembelian.id,
    ))

    pembelian.status = "confirmed"
    db.commit()
    db.refresh(pembelian)
    return pembelian
