# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
source venv/bin/activate
uvicorn main:app --reload             # dev server → http://localhost:8000
uvicorn main:app --host 0.0.0.0 --reload  # accessible on LAN
alembic revision --autogenerate -m "description"
alembic upgrade head
python seed.py                        # idempotent sample data
pytest tests/ -v                      # full test suite (50 tests)
pytest tests/test_kasir.py -v        # single file
```

API docs always available at `http://localhost:8000/docs` when server is running.

## Environment

Copy `.env.example` to `.env` before first run. Two variables:
- `SECRET_KEY` — JWT signing key (64-char random hex recommended)
- `DATABASE_URL` — defaults to `sqlite:///./cashier.db`; swap for PostgreSQL URL

Both `database.py` and `dependencies.py` call `load_dotenv()` at import time.

## Architecture

Single FastAPI monolith. All modules share one SQLite database (`cashier.db`).

**Request flow:** `routers/` → `services/` → `models/` → DB. Routers contain no business logic — they only validate input and call services.

**DB session:** always injected via `Depends(get_db)` from `dependencies.py`. Never instantiate `SessionLocal` directly in routers.

**Auth:** `Depends(get_current_user)` for any authenticated route. `Depends(require_role("admin", "owner"))` for owner/admin-only routes. Kasir role can only access `/kasir` and read `/master/barang`.

**Public endpoint:** `GET /setting/public` — no auth required, used by login page to show store name.

**CORS:** `main.py` uses `allow_origin_regex` to accept any private LAN origin (`192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`) plus localhost, on any port. This allows phone/tablet access on the same Wi-Fi without hardcoding IPs. Do not replace with a fixed `allow_origins` list.

## Key Business Logic

**Tiered pricing** (`services/pricing.py`): `resolve_price(barang, qty)` — checks `min_qty_harga_3` first, then `min_qty_harga_2`, falls back to `harga_1`. Tier disabled when `min_qty` is 0.

**Transaction commit order** (`services/transaksi.py`): must follow this exact sequence within one DB transaction:
1. Validate: cart not empty, `bayar >= total`
2. Insert `Transaksi` header
3. Insert `TransaksiDetail` rows
4. Decrement stock via `services/stok.decrement()` — raises HTTP 400 if stock goes negative
5. Post income entry to `keuangan`
6. `db.commit()`
7. Print receipt (after commit — printer failure is non-fatal)

**Transaction number format:** `TRX-YYYYMMDD-NNN` (daily sequence), generated in `services/transaksi._generate_no()`.

**Purchase confirm flow** (`routers/purchas.py`): on `POST /{id}/confirm` — increment stock for each detail row, post kredit entry to keuangan, set status to `confirmed`. Idempotency check: raise 400 if already confirmed.

**Stock guard** (`services/stok.py`): `decrement()` raises HTTP 400 with the item name when stock would go below zero.

## Models

All in `models/`. Imported together in `models/__init__.py` so Alembic sees them via `import models` in `alembic/env.py`.

Core tables: `user`, `barang`, `kategori`, `supplier`, `transaksi`, `transaksi_detail`, `pembelian`, `pembelian_detail`, `keuangan`, `setting`.

`setting` table always has exactly one row (`id=1`). Use `_get_or_create()` pattern in `routers/setting.py`.

## Printer

`printer.py` — called after transaction commit. Reads `Setting` row for port and paper width. Raises `RuntimeError` if port not configured. Caller (`routers/kasir.py`) catches and ignores printer errors — transaction is already saved.

## Tests

`tests/` — 50 tests, all passing. Uses `StaticPool` in `conftest.py` so all operations share one in-memory SQLite connection (required in SQLAlchemy 2.0 — without it, connections after `commit()` get a fresh empty DB).

Helper functions in `conftest.py`: `make_user()`, `make_barang()`, `make_supplier()`, `make_kategori()`, `auth()`.

## Python Version

Python 3.9. Do NOT use `X | Y` union syntax — use `Optional[X]` from `typing` instead. `list[X]` is fine (PEP 585 supported in 3.9).
