import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cashier.db")

DB_FILE_PATH = (
    os.path.abspath(SQLALCHEMY_DATABASE_URL[len("sqlite:///"):])
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///")
    else None
)
PENDING_RESTORE_PATH = f"{DB_FILE_PATH}.restore_pending" if DB_FILE_PATH else None

# Swap in a staged restore before the engine ever opens the file — the DB
# can't be replaced while a connection holds it open, so restore is staged
# to a side file and applied here, once, before anything connects.
if PENDING_RESTORE_PATH and os.path.exists(PENDING_RESTORE_PATH):
    os.replace(PENDING_RESTORE_PATH, DB_FILE_PATH)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
