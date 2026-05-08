from tests.conftest import make_user, auth


def test_login_success(client, db):
    make_user(db, "kasir1", role="kasir", password="secret")
    res = client.post("/auth/login", json={"username": "kasir1", "password": "secret"})
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert body["user"]["username"] == "kasir1"
    assert body["user"]["role"] == "kasir"


def test_login_wrong_password(client, db):
    make_user(db, "kasir1", password="correct")
    res = client.post("/auth/login", json={"username": "kasir1", "password": "wrong"})
    assert res.status_code == 401


def test_login_unknown_user(client, db):
    res = client.post("/auth/login", json={"username": "nobody", "password": "x"})
    assert res.status_code == 401


def test_login_inactive_user(client, db):
    from models.user import User
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    u = User(username="inactive", password=pwd.hash("pass"), nama="Inactive", role="kasir", is_active=False)
    db.add(u)
    db.commit()
    res = client.post("/auth/login", json={"username": "inactive", "password": "pass"})
    assert res.status_code == 403


def test_protected_route_no_token(client):
    res = client.get("/master/barang")
    assert res.status_code == 401


def test_protected_route_with_valid_token(client, db):
    user = make_user(db, "owner1", role="owner")
    res = client.get("/master/barang", headers=auth(user))
    assert res.status_code == 200


def test_protected_route_invalid_token(client):
    res = client.get("/master/barang", headers={"Authorization": "Bearer notavalidtoken"})
    assert res.status_code == 401
