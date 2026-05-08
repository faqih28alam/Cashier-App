from tests.conftest import make_user, make_barang, make_kategori, auth

BARANG_PAYLOAD = {
    "barcode": "8991101000001",
    "nama_barang": "Aqua 600ml",
    "sat": "BTL",
    "hpp": 2500,
    "harga_1": 3500,
    "harga_2": 3200,
    "min_qty_harga_2": 12,
    "harga_3": 3000,
    "min_qty_harga_3": 24,
    "stok": 50,
    "stok_minimum": 10,
}


# ── Barang ────────────────────────────────────────────────────────────────────

def test_list_barang_empty(client, db):
    owner = make_user(db, "owner", role="owner")
    res = client.get("/master/barang", headers=auth(owner))
    assert res.status_code == 200
    assert res.json() == []


def test_create_barang(client, db):
    owner = make_user(db, "owner", role="owner")
    res = client.post("/master/barang", json=BARANG_PAYLOAD, headers=auth(owner))
    assert res.status_code == 200
    assert res.json()["barcode"] == BARANG_PAYLOAD["barcode"]
    assert res.json()["nama_barang"] == "Aqua 600ml"


def test_create_barang_kasir_forbidden(client, db):
    kasir = make_user(db, "kasir1", role="kasir")
    res = client.post("/master/barang", json=BARANG_PAYLOAD, headers=auth(kasir))
    assert res.status_code == 403


def test_get_barang_by_barcode(client, db):
    owner = make_user(db, "owner", role="owner")
    make_barang(db, barcode="8991101000001")
    res = client.get("/master/barang/8991101000001", headers=auth(owner))
    assert res.status_code == 200
    assert res.json()["barcode"] == "8991101000001"


def test_get_barang_not_found(client, db):
    owner = make_user(db, "owner", role="owner")
    res = client.get("/master/barang/0000000000000", headers=auth(owner))
    assert res.status_code == 404


def test_update_barang(client, db):
    owner = make_user(db, "owner", role="owner")
    make_barang(db, barcode="8991101000001")
    res = client.put(
        "/master/barang/8991101000001",
        json={"harga_1": 9000},
        headers=auth(owner),
    )
    assert res.status_code == 200
    assert float(res.json()["harga_1"]) == 9000


def test_delete_barang(client, db):
    owner = make_user(db, "owner", role="owner")
    make_barang(db, barcode="8991101000001")
    res = client.delete("/master/barang/8991101000001", headers=auth(owner))
    assert res.status_code == 204
    # confirm gone
    res2 = client.get("/master/barang/8991101000001", headers=auth(owner))
    assert res2.status_code == 404


def test_list_barang_search(client, db):
    owner = make_user(db, "owner", role="owner")
    make_barang(db, barcode="1111111111111")
    res = client.get("/master/barang?q=Test", headers=auth(owner))
    assert res.status_code == 200
    assert len(res.json()) == 1


# ── Kategori ──────────────────────────────────────────────────────────────────

def test_list_kategori(client, db):
    owner = make_user(db, "owner", role="owner")
    make_kategori(db)
    res = client.get("/master/kategori", headers=auth(owner))
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_create_kategori(client, db):
    owner = make_user(db, "owner", role="owner")
    res = client.post("/master/kategori", json={"kode_kategori": "MIN", "nama_kategori": "Minuman"}, headers=auth(owner))
    assert res.status_code == 200
    assert res.json()["kode_kategori"] == "MIN"


# ── User management ───────────────────────────────────────────────────────────

def test_list_users(client, db):
    owner = make_user(db, "owner", role="owner")
    make_user(db, "kasir1", role="kasir")
    res = client.get("/master/user", headers=auth(owner))
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_create_user(client, db):
    owner = make_user(db, "owner", role="owner")
    res = client.post(
        "/master/user",
        json={"username": "newkasir", "password": "pass123", "nama": "New Kasir", "role": "kasir"},
        headers=auth(owner),
    )
    assert res.status_code == 200
    assert res.json()["username"] == "newkasir"
    assert res.json()["role"] == "kasir"


def test_update_user(client, db):
    owner = make_user(db, "owner", role="owner")
    target = make_user(db, "kasir1", role="kasir")
    res = client.put(f"/master/user/{target.id}", json={"nama": "Budi Updated"}, headers=auth(owner))
    assert res.status_code == 200
    assert res.json()["nama"] == "Budi Updated"


def test_delete_user(client, db):
    owner = make_user(db, "owner", role="owner")
    target = make_user(db, "kasir1", role="kasir")
    res = client.delete(f"/master/user/{target.id}", headers=auth(owner))
    assert res.status_code == 204


def test_cannot_delete_self(client, db):
    owner = make_user(db, "owner", role="owner")
    res = client.delete(f"/master/user/{owner.id}", headers=auth(owner))
    assert res.status_code == 400


def test_kasir_cannot_list_users(client, db):
    kasir = make_user(db, "kasir1", role="kasir")
    res = client.get("/master/user", headers=auth(kasir))
    assert res.status_code == 403
