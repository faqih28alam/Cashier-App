# Backend — Cashier App

FastAPI backend for the Cashier App POS system. Runs locally on `http://localhost:8000`.

## Stack

| | |
|---|---|
| Framework | FastAPI + Pydantic v2 |
| ORM | SQLAlchemy 2 + Alembic |
| Database | SQLite (`cashier.db`) |
| Auth | JWT via `python-jose` + `passlib[bcrypt]` |
| Printer | `python-escpos` (ESC/POS thermal) |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head             # creates cashier.db with all tables
uvicorn main:app --reload        # starts on http://localhost:8000
```

## API Docs

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Swagger UI — interactive API explorer |
| `http://localhost:8000/redoc` | ReDoc — alternative API docs |

## Commands

```bash
# Run dev server
uvicorn main:app --reload

# Create a new migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

## Project Structure

```
backend/
├── main.py              # App entry point, mounts all routers
├── database.py          # SQLite engine + SessionLocal
├── dependencies.py      # get_db, get_current_user, require_role()
├── printer.py           # ESC/POS receipt builder (python-escpos)
├── requirements.txt
├── alembic.ini
├── alembic/
│   └── versions/        # Migration files
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response schemas
├── routers/             # HTTP endpoints (one file per module)
└── services/            # Business logic (pricing, stok, transaksi, laporan)
```

## Routers & Endpoints

| Router | Prefix | Key Endpoints |
|---|---|---|
| auth | `/auth` | `POST /login` |
| kasir | `/kasir` | `POST /transaksi`, `GET /session` |
| master | `/master` | CRUD `/barang`, `/kategori`, `/supplier`, `/user` |
| purchas | `/purchas` | `POST /`, `POST /{id}/confirm` |
| keuangan | `/keuangan` | `GET /`, `POST /` |
| laporan | `/laporan` | `GET /penjualan`, `/produk-terlaris`, `/stok` |
| setting | `/setting` | `GET /`, `PUT /` |
| print | `/print` | `POST /receipt/{transaksi_id}` |

## User Roles

| Role | Access |
|---|---|
| `kasir` | `/kasir`, `/master/barang` (read) |
| `admin` | All modules |
| `owner` | All modules |
