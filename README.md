# Cashier App — Renal

A web-based Point of Sale (POS) system for retail stores. Runs offline on localhost, accessible from any device on the same local network.

---

## Architecture

```
Cashier PC
├── frontend  (Next.js)      → http://localhost:3000
└── backend   (FastAPI)      → http://localhost:8000
         │
         ├── cashier.db  (SQLite)
         └── thermal printer  (ESC/POS via USB/Serial)

Owner's Phone / Laptop (same WiFi)
└── http://192.168.x.x:3000  → analytics & reports
```

---

## Project Structure

```
cashier-app/
│
├── frontend/                          # Next.js (App Router) + TypeScript + Tailwind
│   ├── app/
│   │   ├── layout.tsx                 # root layout, nav bar, auth guard
│   │   ├── page.tsx                   # redirect to /kasir
│   │   │
│   │   ├── (auth)/
│   │   │   └── login/
│   │   │       └── page.tsx
│   │   │
│   │   ├── kasir/                     # POS — main cashier screen
│   │   │   └── page.tsx
│   │   │
│   │   ├── purchas/                   # Purchasing — incoming stock
│   │   │   ├── page.tsx               # purchase list
│   │   │   └── [id]/page.tsx          # purchase form (new / edit)
│   │   │
│   │   ├── keuangan/                  # Finance — cash flow ledger
│   │   │   └── page.tsx
│   │   │
│   │   ├── laporan/                   # Reports + analytics charts
│   │   │   ├── page.tsx               # dashboard overview
│   │   │   ├── penjualan/page.tsx     # sales report
│   │   │   ├── stok/page.tsx          # stock report
│   │   │   └── transaksi/page.tsx     # transaction log
│   │   │
│   │   ├── master/                    # Master data CRUD
│   │   │   ├── barang/page.tsx        # products
│   │   │   ├── supplier/page.tsx      # suppliers
│   │   │   ├── kategori/page.tsx      # categories
│   │   │   └── user/page.tsx          # user management
│   │   │
│   │   └── setting/
│   │       └── page.tsx               # store info, printer, scanner config
│   │
│   ├── components/
│   │   ├── pos/
│   │   │   ├── TransactionTable.tsx   # scrollable item rows
│   │   │   ├── NumpadPopup.tsx        # qty input overlay
│   │   │   ├── PaymentScreen.tsx      # pembayaran modal
│   │   │   ├── ReceiptPreview.tsx     # receipt popup after payment
│   │   │   ├── BarcodeInput.tsx       # auto-focused scanner input
│   │   │   └── ActionPanel.tsx        # right sidebar buttons + BAYAR
│   │   │
│   │   └── shared/
│   │       ├── Navbar.tsx
│   │       ├── DataTable.tsx          # reusable table for all modules
│   │       ├── Modal.tsx
│   │       └── Toast.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                     # axios/fetch wrapper → localhost:8000
│   │   └── auth.ts                    # JWT helpers
│   │
│   ├── middleware.ts                  # role-based route protection
│   └── .env.local                     # NEXT_PUBLIC_API_URL=http://localhost:8000
│
│
├── backend/                           # FastAPI — monolith, one process
│   ├── main.py                        # mounts all routers, CORS config
│   ├── database.py                    # SQLite engine + session factory
│   ├── dependencies.py                # get_db, get_current_user
│   │
│   ├── routers/                       # HTTP layer only — no business logic here
│   │   ├── auth.py                    # POST /auth/login, /auth/logout
│   │   ├── kasir.py                   # POST /kasir/transaksi, GET /kasir/session
│   │   ├── purchas.py                 # CRUD /purchas/
│   │   ├── keuangan.py                # GET/POST /keuangan/
│   │   ├── laporan.py                 # GET /laporan/penjualan, /stok, etc.
│   │   ├── master.py                  # CRUD /master/barang, /supplier, etc.
│   │   └── setting.py                 # GET/PUT /setting/
│   │
│   ├── services/                      # business logic, called by routers
│   │   ├── transaksi.py               # commit order: save → finance → stock → print
│   │   ├── pricing.py                 # tiered price selection (harga 1/2/3)
│   │   ├── stok.py                    # increment / decrement stock
│   │   └── laporan.py                 # report queries + aggregations
│   │
│   ├── models/                        # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── barang.py
│   │   ├── transaksi.py               # header + detail
│   │   ├── pembelian.py               # header + detail
│   │   ├── keuangan.py
│   │   ├── supplier.py
│   │   ├── kategori.py
│   │   └── setting.py
│   │
│   ├── schemas/                       # Pydantic request / response models
│   │   ├── transaksi.py
│   │   ├── barang.py
│   │   └── ...
│   │
│   ├── printer.py                     # python-escpos — builds + sends receipt
│   │
│   ├── alembic/                       # DB migrations
│   │   └── versions/
│   │
│   ├── alembic.ini
│   └── requirements.txt
│
├── CLAUDE.md                          # guidance for Claude Code
├── PRD_Cashier_App.md                 # full product requirements
├── UI_Reference.pdf                   # original UI design reference
└── UI_Reference.docx
```

---

## Data Flow

```
[Browser — barcode input focused]
        │  keystrokes from USB HID scanner
        ▼
[BarcodeInput.tsx]  →  GET /master/barang/{barcode}
        │
        ▼
[TransactionTable] ← pricing.py selects harga_1/2/3 based on qty
        │
  user clicks BAYAR
        ▼
[PaymentScreen]  →  POST /kasir/transaksi
                          │
                          ├── 1. save transaksi + detail rows  (SQLite)
                          ├── 2. post income to keuangan
                          ├── 3. decrement stok per item
                          └── 4. POST /print/receipt  →  printer.py  →  ESC/POS
                                        │
                                        ▼
                               [ReceiptPreview popup]
```

---

## Modules & Routes

| Module | Frontend | Backend Router |
|---|---|---|
| POS | `/kasir` | `/kasir` |
| Purchasing | `/purchas` | `/purchas` |
| Finance | `/keuangan` | `/keuangan` |
| Reports | `/laporan` | `/laporan` |
| Master Data | `/master` | `/master` |
| Settings | `/setting` | `/setting` |
| Auth | `/login` | `/auth` |

---

## Getting Started

```bash
# 1. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (API explorer)

# 2. Frontend
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## Access on Local Network

```bash
# find your local IP
ipconfig getifaddr en0          # macOS
ipconfig | findstr IPv4         # Windows

# owner opens on phone/laptop (same WiFi):
http://192.168.x.x:3000/laporan
```
