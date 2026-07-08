import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from limiter import limiter
from routers import auth, kasir, purchas, keuangan, laporan, master, setting, print_receipt, backup

app = FastAPI(title="Cashier App API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,           prefix="/auth",    tags=["Auth"])
app.include_router(kasir.router,          prefix="/kasir",   tags=["Kasir"])
app.include_router(purchas.router,        prefix="/purchas", tags=["Purchas"])
app.include_router(keuangan.router,       prefix="/keuangan",tags=["Keuangan"])
app.include_router(laporan.router,        prefix="/laporan", tags=["Laporan"])
app.include_router(master.router,         prefix="/master",  tags=["Master"])
app.include_router(setting.router,        prefix="/setting", tags=["Setting"])
app.include_router(print_receipt.router,  prefix="/print",   tags=["Print"])
app.include_router(backup.router,         prefix="/backup",  tags=["Backup"])


os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}
