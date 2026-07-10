import os
import sqlite3
import tempfile
from pathlib import Path
from typing import List

import httpx

from database import DB_FILE_PATH, PENDING_RESTORE_PATH

BACKUP_SERVICE_URL = os.getenv("BACKUP_SERVICE_URL", "").rstrip("/")
SQLITE_MAGIC = b"SQLite format 3\x00"


def _client() -> httpx.Client:
    if not BACKUP_SERVICE_URL:
        raise RuntimeError("BACKUP_SERVICE_URL belum dikonfigurasi")
    return httpx.Client(base_url=BACKUP_SERVICE_URL, timeout=30.0)


def _detail(res: httpx.Response, fallback: str) -> str:
    try:
        return res.json().get("detail", fallback)
    except ValueError:
        return fallback


def _unreachable(e: httpx.HTTPError) -> RuntimeError:
    return RuntimeError(f"Tidak bisa menghubungi layanan backup: {e}")


def login(client_id: str, password: str) -> str:
    try:
        with _client() as c:
            res = c.post("/auth/login", json={"client_id": client_id, "password": password})
    except httpx.HTTPError as e:
        raise _unreachable(e) from e
    if res.status_code != 200:
        raise ValueError(_detail(res, "Login gagal"))
    return res.json()["access_token"]


def change_password(token: str, old_password: str, new_password: str) -> None:
    try:
        with _client() as c:
            res = c.post(
                "/auth/change-password",
                headers={"Authorization": f"Bearer {token}"},
                json={"old_password": old_password, "new_password": new_password},
            )
    except httpx.HTTPError as e:
        raise _unreachable(e) from e
    if res.status_code != 200:
        raise ValueError(_detail(res, "Gagal mengubah password"))


def snapshot_db_bytes() -> bytes:
    """Consistent point-in-time copy via SQLite's online backup API — safe
    to call even while the app has open connections/transactions, unlike a
    raw file copy which could capture a half-written page.
    """
    if not DB_FILE_PATH:
        raise RuntimeError("Backup hanya didukung untuk database SQLite")
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        try:
            src = sqlite3.connect(f"{Path(DB_FILE_PATH).as_uri()}?mode=ro", uri=True)
            dst = sqlite3.connect(tmp.name)
            try:
                src.backup(dst)
            finally:
                dst.close()
                src.close()
        except sqlite3.Error as e:
            raise RuntimeError(f"Gagal membaca file database: {e}") from e
        tmp.seek(0)
        return tmp.read()


def upload_backup(token: str) -> dict:
    content = snapshot_db_bytes()
    try:
        with _client() as c:
            res = c.post(
                "/backup",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("cashier.db", content, "application/octet-stream")},
            )
    except httpx.HTTPError as e:
        raise _unreachable(e) from e
    if res.status_code != 200:
        raise ValueError(_detail(res, "Backup gagal"))
    return res.json()


def list_backups(token: str) -> List[dict]:
    try:
        with _client() as c:
            res = c.get("/backups", headers={"Authorization": f"Bearer {token}"})
    except httpx.HTTPError as e:
        raise _unreachable(e) from e
    if res.status_code != 200:
        raise ValueError(_detail(res, "Gagal mengambil daftar backup"))
    return res.json()


def download_backup(token: str, filename: str) -> bytes:
    try:
        with _client() as c:
            res = c.get(f"/backup/{filename}", headers={"Authorization": f"Bearer {token}"})
    except httpx.HTTPError as e:
        raise _unreachable(e) from e
    if res.status_code != 200:
        raise ValueError(_detail(res, "Backup tidak ditemukan"))
    return res.content


def stage_restore(content: bytes) -> None:
    if not DB_FILE_PATH or not PENDING_RESTORE_PATH:
        raise RuntimeError("Restore hanya didukung untuk database SQLite")
    if content[:16] != SQLITE_MAGIC:
        raise ValueError("File backup tidak valid")
    with open(PENDING_RESTORE_PATH, "wb") as f:
        f.write(content)
