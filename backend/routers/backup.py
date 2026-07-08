from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from dependencies import get_db, require_role
from models.setting import Setting
from models.user import User
from schemas.backup import (
    BackupChangePasswordRequest,
    BackupFileInfo,
    BackupLoginRequest,
    BackupStatusOut,
)
from services import backup_client

router = APIRouter()


def _get_setting(db: Session) -> Setting:
    setting = db.get(Setting, 1)
    if not setting:
        setting = Setting(id=1)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


def _require_token(setting: Setting) -> str:
    if not setting.backup_token:
        raise HTTPException(status_code=400, detail="Belum login ke layanan backup")
    return setting.backup_token


@router.get("/status", response_model=BackupStatusOut)
def get_status(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    setting = _get_setting(db)
    return BackupStatusOut(connected=bool(setting.backup_token), client_id=setting.backup_client_id)


@router.post("/login", response_model=BackupStatusOut)
def login(
    payload: BackupLoginRequest,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    try:
        token = backup_client.login(payload.client_id, payload.password)
    except (ValueError, RuntimeError) as e:
        # 400, not 401 — this is the backup service rejecting client_id/password,
        # unrelated to the user's own app session. A 401 here would trip api.ts's
        # global "session expired" handler and log the user out of the whole app.
        raise HTTPException(status_code=400, detail=str(e))
    setting = _get_setting(db)
    setting.backup_token = token
    setting.backup_client_id = payload.client_id
    db.commit()
    return BackupStatusOut(connected=True, client_id=payload.client_id)


@router.post("/logout")
def logout(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    setting = _get_setting(db)
    setting.backup_token = None
    setting.backup_client_id = None
    db.commit()
    return {"message": "Logout dari layanan backup"}


@router.post("/change-password")
def change_password(
    payload: BackupChangePasswordRequest,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    setting = _get_setting(db)
    token = _require_token(setting)
    try:
        backup_client.change_password(token, payload.old_password, payload.new_password)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Password backup berhasil diubah"}


@router.post("/now", response_model=BackupFileInfo)
def backup_now(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    setting = _get_setting(db)
    token = _require_token(setting)
    try:
        info = backup_client.upload_backup(token)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return BackupFileInfo(**info)


@router.get("/list", response_model=List[BackupFileInfo])
def get_backup_list(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    setting = _get_setting(db)
    token = _require_token(setting)
    try:
        return backup_client.list_backups(token)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/download/{filename}")
def download_backup(
    filename: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    setting = _get_setting(db)
    token = _require_token(setting)
    try:
        content = backup_client.download_backup(token, filename)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/restore/{filename}")
def restore_backup(
    filename: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("owner"))],
):
    setting = _get_setting(db)
    token = _require_token(setting)
    try:
        content = backup_client.download_backup(token, filename)
        backup_client.stage_restore(content)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Restore disiapkan. Restart aplikasi (jalankan ulang start.bat) untuk menerapkan."}
