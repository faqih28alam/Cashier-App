import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext
from jose import jwt

import models  # registers all ORM models with Base.metadata
from database import Base
from main import app
from dependencies import get_db, SECRET_KEY, ALGORITHM
from models.user import User
from models.barang import Barang
from models.kategori import Kategori
from models.supplier import Supplier

TEST_DB_URL = "sqlite:///:memory:"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture()
def db():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    session = Session()

    def _override():
        yield session

    app.dependency_overrides[get_db] = _override
    yield session
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def client(db):
    return TestClient(app)


# ── helpers ───────────────────────────────────────────────────────────────────

def make_user(db, username: str, role: str = "kasir", password: str = "pass123") -> User:
    u = User(
        username=username,
        password=pwd_context.hash(password),
        nama=username.title(),
        role=role,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def make_token(user: User) -> str:
    return jwt.encode(
        {"sub": str(user.id), "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def auth(user: User) -> dict:
    return {"Authorization": f"Bearer {make_token(user)}"}


def make_barang(db, barcode: str = "8991101000001", stok: int = 20) -> Barang:
    b = Barang(
        barcode=barcode,
        nama_barang="Test Barang",
        sat="PCS",
        hpp=Decimal("5000"),
        harga_1=Decimal("8000"),
        harga_2=Decimal("7500"),
        min_qty_harga_2=5,
        harga_3=Decimal("7000"),
        min_qty_harga_3=10,
        stok=Decimal(str(stok)),
        stok_minimum=Decimal("2"),
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def make_kategori(db) -> Kategori:
    k = Kategori(kode_kategori="TST", nama_kategori="Test Kategori")
    db.add(k)
    db.commit()
    db.refresh(k)
    return k


def make_supplier(db) -> Supplier:
    s = Supplier(kode_supplier="SUP-T01", nama_supplier="Test Supplier")
    db.add(s)
    db.commit()
    db.refresh(s)
    return s
