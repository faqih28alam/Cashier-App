from decimal import Decimal
from tests.conftest import make_user, make_barang, make_supplier, auth
from models.keuangan import Keuangan
from models.pembelian import Pembelian


def _po_payload(supplier_id, barcode):
    return {
        "no_faktur": "PO-TEST-001",
        "tanggal": "2026-05-09T00:00:00",
        "id_supplier": supplier_id,
        "detail": [
            {"barcode": barcode, "nama_barang": "Test Barang", "sat": "PCS", "qty": 10, "hpp": 5000},
        ],
    }


def test_create_draft_purchase(client, db):
    owner = make_user(db, "owner", role="owner")
    sup = make_supplier(db)
    barang = make_barang(db, stok=20)

    res = client.post("/purchas/", json=_po_payload(sup.id, barang.barcode), headers=auth(owner))
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "draft"
    assert body["no_faktur"] == "PO-TEST-001"
    assert float(body["total"]) == 10 * 5000

    # stock must NOT change yet
    db.refresh(barang)
    assert barang.stok == Decimal("20")


def test_confirm_purchase_updates_stock(client, db):
    owner = make_user(db, "owner", role="owner")
    sup = make_supplier(db)
    barang = make_barang(db, stok=20)

    # create draft
    res = client.post("/purchas/", json=_po_payload(sup.id, barang.barcode), headers=auth(owner))
    po_id = res.json()["id"]

    # confirm
    res2 = client.post(f"/purchas/{po_id}/confirm", json={}, headers=auth(owner))
    assert res2.status_code == 200
    assert res2.json()["status"] == "confirmed"

    # stock must increase by qty (10)
    db.refresh(barang)
    assert barang.stok == Decimal("30")


def test_confirm_creates_keuangan_entry(client, db):
    owner = make_user(db, "owner", role="owner")
    sup = make_supplier(db)
    barang = make_barang(db, stok=5)

    res = client.post("/purchas/", json=_po_payload(sup.id, barang.barcode), headers=auth(owner))
    po_id = res.json()["id"]
    client.post(f"/purchas/{po_id}/confirm", json={}, headers=auth(owner))

    entry = db.query(Keuangan).filter(Keuangan.ref_type == "pembelian", Keuangan.ref_id == po_id).first()
    assert entry is not None
    assert float(entry.kredit) == 10 * 5000
    assert float(entry.debit) == 0


def test_cannot_confirm_twice(client, db):
    owner = make_user(db, "owner", role="owner")
    sup = make_supplier(db)
    barang = make_barang(db, stok=5)

    res = client.post("/purchas/", json=_po_payload(sup.id, barang.barcode), headers=auth(owner))
    po_id = res.json()["id"]
    client.post(f"/purchas/{po_id}/confirm", json={}, headers=auth(owner))
    res2 = client.post(f"/purchas/{po_id}/confirm", json={}, headers=auth(owner))
    assert res2.status_code == 400


def test_kasir_cannot_create_purchase(client, db):
    kasir = make_user(db, "kasir1", role="kasir")
    sup = make_supplier(db)
    barang = make_barang(db)
    res = client.post("/purchas/", json=_po_payload(sup.id, barang.barcode), headers=auth(kasir))
    assert res.status_code == 403


def test_list_purchases(client, db):
    owner = make_user(db, "owner", role="owner")
    res = client.get("/purchas/", headers=auth(owner))
    assert res.status_code == 200
    assert isinstance(res.json(), list)
