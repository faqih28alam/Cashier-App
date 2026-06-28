from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from models.transaksi import Transaksi, TransaksiDetail
from models.barang import Barang
from models.user import User


def penjualan_harian(db: Session, tgl_mulai: date, tgl_selesai: date) -> list[dict]:
    rows = (
        db.query(
            func.date(Transaksi.tanggal).label("tanggal"),
            func.count(func.distinct(Transaksi.id)).label("jumlah_transaksi"),
            func.sum(TransaksiDetail.total).label("total_penjualan"),
            func.sum(
                TransaksiDetail.total - TransaksiDetail.hpp * TransaksiDetail.qty
            ).label("laba_kotor"),
        )
        .join(TransaksiDetail, TransaksiDetail.id_transaksi == Transaksi.id)
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


def penjualan_detail(db: Session, tgl_mulai: date, tgl_selesai: date) -> list[dict]:
    rows = (
        db.query(
            TransaksiDetail.id.label("id"),
            Transaksi.id.label("transaksi_id"),
            func.date(Transaksi.tanggal).label("tanggal"),
            Transaksi.no_transaksi,
            TransaksiDetail.nama_barang,
            TransaksiDetail.sat,
            TransaksiDetail.qty,
            TransaksiDetail.hpp,
            TransaksiDetail.harga,
            TransaksiDetail.diskon,
            TransaksiDetail.total,
            (TransaksiDetail.total - TransaksiDetail.hpp * TransaksiDetail.qty).label("laba_kotor"),
        )
        .join(TransaksiDetail, TransaksiDetail.id_transaksi == Transaksi.id)
        .filter(
            Transaksi.status == "paid",
            func.date(Transaksi.tanggal) >= tgl_mulai,
            func.date(Transaksi.tanggal) <= tgl_selesai,
        )
        .order_by(Transaksi.tanggal.desc(), Transaksi.id, TransaksiDetail.id)
        .all()
    )
    return [r._asdict() for r in rows]


def stok_list(db: Session) -> list[Barang]:
    return db.query(Barang).order_by(Barang.nama_barang).all()


def transaksi_list(db: Session, tgl_mulai: date, tgl_selesai: date) -> list[dict]:
    rows = (
        db.query(Transaksi)
        .options(joinedload(Transaksi.detail), joinedload(Transaksi.user))
        .filter(
            Transaksi.status == "paid",
            func.date(Transaksi.tanggal) >= tgl_mulai,
            func.date(Transaksi.tanggal) <= tgl_selesai,
        )
        .order_by(Transaksi.tanggal.desc())
        .all()
    )
    result = []
    for t in rows:
        result.append({
            "id": t.id,
            "no_transaksi": t.no_transaksi,
            "tanggal": t.tanggal.isoformat(),
            "kasir": t.user.nama if t.user else "-",
            "total": float(t.total),
            "bayar": float(t.bayar),
            "kembalian": float(t.kembalian),
            "detail": [
                {
                    "nama_barang": d.nama_barang,
                    "qty": float(d.qty),
                    "sat": d.sat,
                    "harga": float(d.harga),
                    "diskon": float(d.diskon),
                    "total": float(d.total),
                }
                for d in t.detail
            ],
        })
    return result
