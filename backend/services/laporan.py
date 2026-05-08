from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.transaksi import Transaksi, TransaksiDetail
from models.barang import Barang


def penjualan_harian(db: Session, tgl_mulai: date, tgl_selesai: date) -> list[dict]:
    rows = (
        db.query(
            func.date(Transaksi.tanggal).label("tanggal"),
            func.count(Transaksi.id).label("jumlah_transaksi"),
            func.sum(Transaksi.total).label("total_penjualan"),
        )
        .filter(
            Transaksi.status == "paid",
            func.date(Transaksi.tanggal) >= tgl_mulai,
            func.date(Transaksi.tanggal) <= tgl_selesai,
        )
        .group_by(func.date(Transaksi.tanggal))
        .order_by(func.date(Transaksi.tanggal))
        .all()
    )
    return [r._asdict() for r in rows]


def produk_terlaris(db: Session, tgl_mulai: date, tgl_selesai: date, limit: int = 10) -> list[dict]:
    rows = (
        db.query(
            TransaksiDetail.barcode,
            TransaksiDetail.nama_barang,
            func.sum(TransaksiDetail.qty).label("total_qty"),
            func.sum(TransaksiDetail.total).label("total_penjualan"),
        )
        .join(Transaksi, Transaksi.id == TransaksiDetail.id_transaksi)
        .filter(
            Transaksi.status == "paid",
            func.date(Transaksi.tanggal) >= tgl_mulai,
            func.date(Transaksi.tanggal) <= tgl_selesai,
        )
        .group_by(TransaksiDetail.barcode, TransaksiDetail.nama_barang)
        .order_by(func.sum(TransaksiDetail.qty).desc())
        .limit(limit)
        .all()
    )
    return [r._asdict() for r in rows]


def stok_list(db: Session) -> list[Barang]:
    return db.query(Barang).order_by(Barang.nama_barang).all()
