"""Tests for pure business logic in services/."""
from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from database import Base
from models.barang import Barang
from models.barang_harga import BarangHarga
from services.pricing import resolve_price
from services import stok as stok_service

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture()
def session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    s = Session()
    yield s
    s.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _barang(session, barcode="B001", harga_1=8000, harga_2=7500, min2=5, harga_3=7000, min3=10, stok=20):
    b = Barang(
        barcode=barcode,
        nama_barang="Test",
        sat="PCS",
        hpp=Decimal("5000"),
        harga_1=Decimal(str(harga_1)),
        stok=Decimal(str(stok)),
        stok_minimum=Decimal("2"),
    )
    session.add(b)
    session.flush()
    if min2 > 0:
        session.add(BarangHarga(barcode=barcode, min_qty=Decimal(str(min2)), harga=Decimal(str(harga_2))))
    if min3 > 0:
        session.add(BarangHarga(barcode=barcode, min_qty=Decimal(str(min3)), harga=Decimal(str(harga_3))))
    session.commit()
    session.refresh(b)
    return b


# ── Pricing ───────────────────────────────────────────────────────────────────

class TestResolvePrice:
    def test_eceran_returns_harga_1(self, session):
        b = _barang(session, min2=5, min3=10)
        assert resolve_price(b, Decimal("1")) == Decimal("8000")
        assert resolve_price(b, Decimal("4")) == Decimal("8000")

    def test_grosir_2_returns_harga_2(self, session):
        b = _barang(session, min2=5, min3=10)
        assert resolve_price(b, Decimal("5")) == Decimal("7500")
        assert resolve_price(b, Decimal("9")) == Decimal("7500")

    def test_grosir_3_returns_harga_3(self, session):
        b = _barang(session, min2=5, min3=10)
        assert resolve_price(b, Decimal("10")) == Decimal("7000")
        assert resolve_price(b, Decimal("100")) == Decimal("7000")

    def test_no_tiers_always_harga_1(self, session):
        b = _barang(session, min2=0, min3=0)
        assert resolve_price(b, Decimal("100")) == Decimal("8000")

    def test_boundary_exactly_at_min_qty(self, session):
        b = _barang(session, min2=12, min3=24)
        assert resolve_price(b, Decimal("11")) == Decimal("8000")
        assert resolve_price(b, Decimal("12")) == Decimal("7500")
        assert resolve_price(b, Decimal("23")) == Decimal("7500")
        assert resolve_price(b, Decimal("24")) == Decimal("7000")


# ── Stock ─────────────────────────────────────────────────────────────────────

class TestStok:
    def test_decrement_reduces_stock(self, session):
        b = _barang(session, stok=20)
        stok_service.decrement(session, b.barcode, Decimal("5"))
        session.refresh(b)
        assert b.stok == Decimal("15")

    def test_increment_increases_stock(self, session):
        b = _barang(session, stok=10)
        stok_service.increment(session, b.barcode, Decimal("12"))
        session.refresh(b)
        assert b.stok == Decimal("22")

    def test_decrement_to_zero(self, session):
        b = _barang(session, stok=5)
        stok_service.decrement(session, b.barcode, Decimal("5"))
        session.refresh(b)
        assert b.stok == Decimal("0")

    def test_multiple_decrements(self, session):
        b = _barang(session, stok=30)
        stok_service.decrement(session, b.barcode, Decimal("10"))
        stok_service.decrement(session, b.barcode, Decimal("5"))
        session.refresh(b)
        assert b.stok == Decimal("15")
