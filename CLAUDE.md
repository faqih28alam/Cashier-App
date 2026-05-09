# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A web-based Point of Sale (POS) system for a retail store. Runs on **localhost** (offline-first), accessible from any device on the same local network — cashier on PC, owner checks analytics on phone/laptop. Full PRD is in `PRD_Cashier_App.md`.

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 15 (App Router) + TypeScript + Tailwind CSS + Recharts |
| Backend | Python FastAPI + Pydantic v2 |
| ORM | SQLAlchemy 2 + Alembic |
| Database | SQLite (local) — swap `DATABASE_URL` in `.env` to migrate to PostgreSQL |
| Thermal Printer | python-escpos |
| Barcode Scanner | USB HID — treated as keyboard input, no backend needed |

## Dev Commands

```bash
# Backend
cd backend
source venv/bin/activate              # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                  # first time only
alembic upgrade head
python seed.py                        # optional sample data
uvicorn main:app --reload             # http://localhost:8000
                                      # http://localhost:8000/docs

# Frontend
cd frontend
npm install
npm run dev                           # http://localhost:3000
npm run build && npm run start        # production mode

# Tests (backend only)
cd backend && pytest tests/ -v
pytest tests/test_kasir.py -v        # single file
pytest tests/ -q                     # quiet summary
```

## Architecture Notes

### Two-process local deployment
Frontend (Next.js) and backend (FastAPI) run as separate processes. Frontend calls backend via `http://localhost:8000`. Configure in `frontend/.env.local` as `NEXT_PUBLIC_API_URL=http://localhost:8000`. On the same LAN, replace `localhost` with the PC's local IP so the owner can access from other devices.

### Environment variables
Backend reads `SECRET_KEY` and `DATABASE_URL` from `backend/.env` via `python-dotenv`. Both `database.py` and `dependencies.py` call `load_dotenv()` at import time. `.env` is gitignored; `.env.example` is the template.

### Auth flow
- Login: `POST /auth/login` → returns JWT with `sub=str(user.id)`
- Frontend stores token in cookie via `lib/auth.ts`
- `api.ts` attaches `Authorization: Bearer <token>` to every request
- 401 with an existing token → `clearAuth()` + redirect to `/login`
- 401 without a token (failed login) → error thrown to the caller (shows toast)
- `middleware.ts` protects routes server-side; `dependencies.py` protects API routes

### Barcode scanner
USB HID mode — sends keystrokes to the focused input. The kasir page keeps the barcode field auto-focused at all times. On Enter, frontend calls `GET /master/barang/{barcode}`. No serial port handling needed.

### Thermal printer
Print jobs go through `POST /print/receipt`. Backend uses python-escpos to send ESC/POS commands. Printer port and paper width are stored in the `setting` table. Printer failures are non-fatal — transaction is already committed before printing is attempted.

### Tiered pricing
`backend/services/pricing.py` — `resolve_price(barang, qty)`:
- qty >= `min_qty_harga_3` → `harga_3`
- qty >= `min_qty_harga_2` → `harga_2`
- otherwise → `harga_1`
- tier disabled when `min_qty` is 0

Mirrored client-side in `resolvePrice()` in `kasir/page.tsx`.

### Transaction commit order
Must follow this exact sequence in one DB transaction:
1. Validate: cart not empty, `bayar >= total`, stock sufficient per item
2. Insert `Transaksi` header
3. Insert `TransaksiDetail` rows
4. Decrement stock via `services/stok.decrement()` — raises 400 if stock goes negative
5. Post income entry to `keuangan`
6. `db.commit()`
7. Print receipt (after commit — printer failure is non-fatal)

### Public setting endpoint
`GET /setting/public` requires no auth — used by the login page to show the store name before the user logs in. `GET /setting/` requires auth.

## Key Business Rules

- **HPP** — cost price, visible in transaction table and reports but never on customer receipt
- **Kembalian** — Bayar − Total; KONFIRMASI disabled if Bayar < Total (enforced both client and server)
- **Stock guard** — `stok.decrement` raises HTTP 400 with item name if stock would go negative
- **Held transaction** — `status = open`, one per cashier session, resumable via session screen
- **Purchase confirm** — increments stock + posts kredit to keuangan; raises 400 if already confirmed
- **Finance entries** — auto-posted from KASIR (debit) and PURCHAS (kredit); manual entries for operational costs

## User Roles

- **Kasir** — `/kasir` only + read `/master/barang`
- **Admin** — all modules
- **Owner** — all modules including financial reports

Role is stored in the JWT `sub` payload. `require_role("admin", "owner")` dependency used on owner/admin-only routes.

## Database

SQLite file at `backend/cashier.db`. Alembic manages migrations (`backend/alembic/`). Switch to PostgreSQL by changing `DATABASE_URL` in `.env` — SQLAlchemy handles the rest.

Core tables: `user`, `barang`, `kategori`, `supplier`, `transaksi`, `transaksi_detail`, `pembelian`, `pembelian_detail`, `keuangan`, `setting`.

`setting` table always has exactly one row (`id=1`). Use `_get_or_create()` pattern in `routers/setting.py`.

## Tests

50 tests across 6 files in `backend/tests/`. Use `StaticPool` (single SQLite connection) to avoid in-memory DB isolation issues across threads. Each test gets a fresh DB via function-scoped `db` fixture that overrides `get_db`.

## Windows Delivery

`setup.bat` — one-time install (venv, deps, migrations, seed, npm build).
`start.bat` — launcher: starts backend + frontend in minimized windows, waits 8s, opens browser.
`README_DELIVERY.md` — bilingual (ID/EN) client installation guide.
