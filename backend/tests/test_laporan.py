import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from tests.conftest import make_user, make_barang, auth
from models.transaksi import Transaksi, TransaksiDetail
from models.keuangan import Keuangan

TODAY = datetime.now().date().isoformat()
MONTH_START = datetime.now().replace(day=1).date().isoformat()


def _seed_transaction(db, user, barang, qty=2, harga=8000):
    """Insert a paid transaction directly into DB."""
    total = qty * harga
    trx = Transaksi(
        no_transaksi=f"TRX-TEST-{uuid.uuid4().hex[:8]}",
        tanggal=datetime.now(),
        id_user=user.id,
        total=Decimal(str(total)),
        bayar=Decimal("50000"),
        kembalian=Decimal(str(50000 - total)),
        status="paid",
    )
    db.add(trx)
    db.flush()
    db.add(TransaksiDetail(
        id_transaksi=trx.id,
        barcode=barang.barcode,
        nama_barang=barang.nama_barang,
        sat=barang.sat,
        qty=Decimal(str(qty)),
        hpp=barang.hpp,
        harga=Decimal(str(harga)),
        diskon=Decimal("0"),
        total=Decimal(str(total)),
    ))
    db.commit()
    return trx


def test_penjualan_harian(client, db):
    owner = make_user(db, "owner", role="owner")
    barang = make_barang(db, stok=50)
    _seed_transaction(db, owner, barang, qty=3, harga=8000)

    res = client.get(
        f"/laporan/penjualan?tgl_mulai={MONTH_START}&tgl_selesai={TODAY}",
        headers=auth(owner),
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["jumlah_transaksi"] == 1
    assert float(data[0]["total_penjualan"]) == 3 * 8000


def test_penjualan_harian_empty_range(client, db):
    owner = make_user(db, "owner", role="owner")
    res = client.get(
        "/laporan/penjualan?tgl_mulai=2020-01-01&tgl_selesai=2020-01-31",
        headers=auth(owner),
    )
    assert res.status_code == 200
    assert res.json() == []


def test_produk_terlaris(client, db):
    owner = make_user(db, "owner", role="owner")
    b1 = make_barang(db, barcode="1111111111111", stok=50)
    b2 = make_barang(db, barcode="2222222222222", stok=50)
    _seed_transaction(db, owner, b1, qty=10, harga=8000)
    _seed_transaction(db, owner, b2, qty=3, harga=8000)

    res = client.get(
        f"/laporan/produk-terlaris?tgl_mulai={MONTH_START}&tgl_selesai={TODAY}&limit=10",
        headers=auth(owner),
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    # highest qty first
    assert float(data[0]["total_qty"]) == 10
    assert float(data[1]["total_qty"]) == 3


def test_riwayat_transaksi(client, db):
    owner = make_user(db, "owner", role="owner")
    barang = make_barang(db, stok=30)
    _seed_transaction(db, owner, barang, qty=2, harga=8000)
    _seed_transaction(db, owner, barang, qty=4, harga=8000)

    res = client.get(
        f"/laporan/transaksi?tgl_mulai={MONTH_START}&tgl_selesai={TODAY}",
        headers=auth(owner),
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    # each has detail
    assert len(data[0]["detail"]) == 1
    assert data[0]["kasir"] == "Owner"


def test_laporan_stok(client, db):
    owner = make_user(db, "owner", role="owner")
    make_barang(db, barcode="1111111111111", stok=15)
    make_barang(db, barcode="2222222222222", stok=3)

    res = client.get("/laporan/stok", headers=auth(owner))
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_kasir_cannot_access_laporan(client, db):
    kasir = make_user(db, "kasir1", role="kasir")
    res = client.get(
        f"/laporan/penjualan?tgl_mulai={MONTH_START}&tgl_selesai={TODAY}",
        headers=auth(kasir),
    )
    assert res.status_code == 403
