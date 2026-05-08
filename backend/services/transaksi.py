from datetime import date, datetime
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.transaksi import Transaksi, TransaksiDetail
from models.keuangan import Keuangan
from schemas.transaksi import TransaksiCreate
from services import stok


def _generate_no(db: Session) -> str:
    today = date.today()
    prefix = f"TRX-{today.strftime('%Y%m%d')}-"
    count = db.query(func.count(Transaksi.id)).filter(
        Transaksi.no_transaksi.like(f"{prefix}%")
    ).scalar()
    return f"{prefix}{str(count + 1).zfill(3)}"


def create(db: Session, payload: TransaksiCreate, user_id: int) -> Transaksi:
    if not payload.detail:
        raise HTTPException(status_code=400, detail="Transaksi harus memiliki minimal satu item")

    total = sum(
        (item.qty * item.harga) - item.diskon for item in payload.detail
    )
    if payload.bayar < total:
        raise HTTPException(
            status_code=400,
            detail=f"Uang bayar kurang dari total ({int(total):,})",
        )

    kembalian = payload.bayar - total

    trx = Transaksi(
        no_transaksi=_generate_no(db),
        tanggal=datetime.now(),
        id_user=user_id,
        total=total,
        bayar=payload.bayar,
        kembalian=kembalian,
        status="paid",
    )
    db.add(trx)
    db.flush()

    for item in payload.detail:
        item_total = (item.qty * item.harga) - item.diskon
        db.add(TransaksiDetail(
            id_transaksi=trx.id,
            barcode=item.barcode,
            nama_barang=item.nama_barang,
            sat=item.sat,
            qty=item.qty,
            hpp=item.hpp,
            harga=item.harga,
            diskon=item.diskon,
            total=item_total,
        ))
        stok.decrement(db, item.barcode, item.qty)

    db.add(Keuangan(
        keterangan=f"Penjualan {trx.no_transaksi}",
        debit=total,
        kredit=Decimal("0"),
        ref_type="transaksi",
        ref_id=trx.id,
    ))

    db.commit()
    db.refresh(trx)
    return trx
