from decimal import Decimal
from tests.conftest import make_user, make_barang, auth
from models.keuangan import Keuangan
from models.transaksi import Transaksi


def _trx_payload(barcode, qty=2, harga=8000):
    return {
        "bayar": 50000,
        "detail": [
            {
                "barcode": barcode,
                "nama_barang": "Test Barang",
                "sat": "PCS",
                "qty": qty,
                "hpp": 5000,
                "harga": harga,
                "diskon": 0,
            }
        ],
    }


def test_create_transaction_success(client, db):
    kasir = make_user(db, "kasir1", role="kasir")
    barang = make_barang(db, stok=20)

    res = client.post("/kasir/transaksi", json=_trx_payload(barang.barcode, qty=2), headers=auth(kasir))
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "paid"
    assert float(body["total"]) == 2 * 8000
    assert float(body["kembalian"]) == 50000 - 2 * 8000
    assert body["no_transaksi"].startswith("TRX-")


def test_transaction_decrements_stock(client, db):
    kasir = make_user(db, "kasir1", role="kasir")
    barang = make_barang(db, stok=20)

    client.post("/kasir/transaksi", json=_trx_payload(barang.barcode, qty=3), headers=auth(kasir))

    db.refresh(barang)
    assert barang.stok == Decimal("17")


def test_transaction_creates_keuangan_entry(client, db):
    kasir = make_user(db, "kasir1", role="kasir")
    barang = make_barang(db, stok=10)

    res = client.post("/kasir/transaksi", json=_trx_payload(barang.barcode, qty=2, harga=8000), headers=auth(kasir))
    trx_id = res.json()["id"]

    entry = db.query(Keuangan).filter(Keuangan.ref_type == "transaksi", Keuangan.ref_id == trx_id).first()
    assert entry is not None
    assert float(entry.debit) == 2 * 8000
    assert float(entry.kredit) == 0


def test_transaction_number_format(client, db):
    kasir = make_user(db, "kasir1", role="kasir")
    barang = make_barang(db, stok=10)

    res = client.post("/kasir/transaksi", json=_trx_payload(barang.barcode), headers=auth(kasir))
    no = res.json()["no_transaksi"]
    # format: TRX-YYYYMMDD-NNN
    parts = no.split("-")
    assert parts[0] == "TRX"
    assert len(parts[1]) == 8   # YYYYMMDD
    assert parts[2].isdigit()


def test_multiple_items_in_transaction(client, db):
    kasir = make_user(db, "kasir1", role="kasir")
    b1 = make_barang(db, barcode="1111111111111", stok=10)
    b2 = make_barang(db, barcode="2222222222222", stok=10)

    payload = {
        "bayar": 100000,
        "detail": [
            {"barcode": b1.barcode, "nama_barang": "Barang 1", "sat": "PCS", "qty": 2, "hpp": 5000, "harga": 8000, "diskon": 0},
            {"barcode": b2.barcode, "nama_barang": "Barang 2", "sat": "PCS", "qty": 3, "hpp": 5000, "harga": 8000, "diskon": 0},
        ],
    }
    res = client.post("/kasir/transaksi", json=payload, headers=auth(kasir))
    assert res.status_code == 200
    assert float(res.json()["total"]) == (2 + 3) * 8000

    db.refresh(b1)
    db.refresh(b2)
    assert b1.stok == Decimal("8")
    assert b2.stok == Decimal("7")


def test_kasir_session_endpoint(client, db):
    kasir = make_user(db, "kasir1", role="kasir")
    res = client.get("/kasir/session", headers=auth(kasir))
    assert res.status_code == 200
    assert "has_held" in res.json()
