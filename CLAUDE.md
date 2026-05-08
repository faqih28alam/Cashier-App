# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A web-based Point of Sale (POS) system for a retail store. Runs on **localhost** (offline-first), accessible from any device on the same local network — cashier on PC, owner checks analytics on phone/laptop. Full PRD is in `PRD_Cashier_App.md`. UI reference screenshots are in `UI_Reference.pdf`.

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js (App Router) + TypeScript + Tailwind CSS + Recharts |
| Backend | Python FastAPI + Pydantic |
| ORM | SQLAlchemy + Alembic |
| Database | SQLite (local) — designed to migrate to PostgreSQL for cloud |
| Thermal Printer | python-escpos |
| Barcode Scanner | USB HID — treated as keyboard input in the browser, no backend needed |

## Planned Project Structure

```
/
├── frontend/               # Next.js app
│   ├── app/
│   │   ├── kasir/          # POS / cashier screen
│   │   ├── purchas/        # Purchasing module
│   │   ├── keuangan/       # Finance module
│   │   ├── laporan/        # Reports + analytics dashboard
│   │   ├── master/         # Master data (products, suppliers, users, categories)
│   │   └── setting/        # App configuration
│   └── components/
│       ├── pos/            # POS-specific: transaction table, numpad popup, payment screen
│       └── shared/         # Shared UI components
│
├── backend/                # FastAPI app
│   ├── main.py
│   ├── routers/            # One router file per module (kasir, purchas, master, etc.)
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── services/           # Business logic (pricing, receipt building, print job)
│   ├── printer.py          # python-escpos integration
│   └── database.py         # SQLite engine + session
│
└── PRD_Cashier_App.md
```

## Dev Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head           # run migrations
uvicorn main:app --reload      # starts on http://localhost:8000
                               # API docs: http://localhost:8000/docs

# Frontend
cd frontend
npm install
npm run dev                    # starts on http://localhost:3000
npm run build && npm run start # production mode

# Run both together (once a script exists)
./start.sh
```

## Architecture Notes

### Two-process local deployment
Frontend (Next.js) and backend (FastAPI) run as separate processes. Frontend calls backend via `http://localhost:8000`. Configure the base URL in `frontend/.env.local` as `NEXT_PUBLIC_API_URL=http://localhost:8000`. On the same LAN, replace `localhost` with the PC's local IP so the owner can access from other devices.

### Barcode scanner
The scanner operates in USB HID mode — it sends keystrokes to whichever input is focused. The POS page keeps the barcode input field auto-focused at all times. On Enter, the frontend calls `GET /api/barang/{barcode}`. No serial port handling needed on the frontend.

### Thermal printer
All print jobs go through the FastAPI backend (`POST /api/print/receipt`). The backend uses `python-escpos` to send ESC/POS commands to the configured printer port. Printer port and paper width (58mm/80mm) are stored in the `setting` table and loaded at startup. If the printer is offline, the API returns a graceful error — the transaction is already saved before printing is attempted.

### Tiered pricing logic
Lives in `backend/services/pricing.py`. When a product's QTY changes, the frontend calls the pricing service (or calculates client-side using product data already fetched). Rules per product:
- QTY < `min_qty_harga_2` → use `harga_1`
- QTY >= `min_qty_harga_2` and < `min_qty_harga_3` → use `harga_2`
- QTY >= `min_qty_harga_3` → use `harga_3`

### Transaction commit order
1. Save transaction header + detail rows to DB (status = `paid`)
2. Post income entry to `keuangan` table
3. Decrement stock for each item
4. Send print job to printer

Never print before step 1–3 are committed. If the printer fails after commit, the transaction is still valid — show a reprint option.

### Transaction number format
`TRX-YYYYMMDD-NNN` where NNN is a daily sequence reset each day. Generated server-side in `backend/services/transaction.py`.

## Key Business Rules

- **HPP** (Harga Pokok Penjualan) is cost price — visible in transaction table and reports but never shown on the customer receipt
- **Kembalian** (change) = Bayar − Total; KONFIRMASI button is disabled if Bayar < Total
- A held transaction (`status = open`) can be resumed via "Lanjutkan Transaksi" on the session screen; only one held transaction per cashier session
- Stock is decremented on transaction confirm, restocked on purchase confirm
- Finance entries are auto-posted from KASIR (income) and PURCHAS (expense/COGS); manual entries for operational costs

## Modules Summary

| Module | Route | Description |
|---|---|---|
| KASIR | `/kasir` | POS screen — the main cashier interface |
| PURCHAS | `/purchas` | Record incoming stock from suppliers |
| KEUANGAN | `/keuangan` | Cash flow ledger |
| LAPORAN | `/laporan` | Reports + analytics charts (Recharts) |
| MASTER | `/master` | CRUD for products, suppliers, categories, users |
| SETTING | `/setting` | Store info, printer port, receipt config |

## User Roles

- **Kasir** — `/kasir` only
- **Admin** — all modules
- **Owner** — all modules including financial reports and analytics

Role is stored in the JWT token issued at login. Middleware on both Next.js (middleware.ts) and FastAPI checks role before serving protected routes.

## Database

SQLite file at `backend/cashier.db`. Alembic manages migrations (`backend/alembic/`). To switch to PostgreSQL, change the `DATABASE_URL` env var — SQLAlchemy dialect handles the rest.

Core tables: `user`, `barang`, `kategori`, `supplier`, `transaksi`, `transaksi_detail`, `pembelian`, `pembelian_detail`, `keuangan`, `setting`.
