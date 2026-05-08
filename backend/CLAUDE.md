# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
source venv/bin/activate
uvicorn main:app --reload          # dev server → http://localhost:8000
alembic revision --autogenerate -m "description"  # new migration
alembic upgrade head               # apply migrations
```

API docs always available at `http://localhost:8000/docs` when server is running.

## Architecture

Single FastAPI monolith. All modules share one SQLite database (`cashier.db`).

**Request flow:** `routers/` → `services/` → `models/` → DB. Routers contain no business logic — they only validate input and call services.

**DB session:** always injected via `Depends(get_db)` from `dependencies.py`. Never instantiate `SessionLocal` directly in routers.

**Auth:** `Depends(get_current_user)` for any authenticated route. `Depends(require_role("admin", "owner"))` for admin-only routes. Kasir role can only access `/kasir` and read `/master/barang`.

## Key Business Logic

**Tiered pricing** (`services/pricing.py`): `resolve_price(barang, qty)` — checks `min_qty_harga_3` first, then `min_qty_harga_2`, falls back to `harga_1`.

**Transaction commit order** (`services/transaksi.py`): must follow this exact sequence within one DB transaction:
1. Insert `Transaksi` header
2. Insert `TransaksiDetail` rows
3. Decrement stock via `services/stok.decrement()`
4. Post income entry to `keuangan`
5. `db.commit()`
6. Print receipt (after commit — printer failure is non-fatal)

Never commit before all 4 steps are done. Never print before commit.

**Transaction number format:** `TRX-YYYYMMDD-NNN` (daily sequence), generated in `services/transaksi._generate_no()`.

**Purchase confirm flow** (`routers/purchas.py`): on `POST /{id}/confirm` — increment stock for each detail row, post kredit entry to keuangan, set status to `confirmed`. Idempotency check: raise 400 if already confirmed.

## Models

All in `models/`. Imported together in `models/__init__.py` so Alembic sees them via `import models` in `alembic/env.py`.

Core tables: `user`, `barang`, `kategori`, `supplier`, `transaksi`, `transaksi_detail`, `pembelian`, `pembelian_detail`, `keuangan`, `setting`.

`setting` table always has exactly one row (`id=1`). Use `_get_or_create()` pattern in `routers/setting.py`.

## Printer

`printer.py` — called after transaction commit. Reads `Setting` row for port and paper width. Raises `RuntimeError` if port not configured. Caller (`routers/kasir.py`) catches and ignores printer errors — transaction is already saved.

## Python Version

Python 3.9. Do NOT use `X | Y` union syntax — use `Optional[X]` from `typing` instead. `list[X]` is fine (PEP 585 supported in 3.9).
