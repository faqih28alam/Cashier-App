import os
import platform
import shutil
import subprocess
from typing import Annotated, List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user, require_role
from models.setting import Setting
from models.user import User
from schemas.setting import SettingOut, SettingUpdate

router = APIRouter()


def _get_or_create(db: Session) -> Setting:
    setting = db.get(Setting, 1)
    if not setting:
        setting = Setting(id=1)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


@router.get("/public", response_model=SettingOut)
def get_setting_public(db: Annotated[Session, Depends(get_db)]):
    return _get_or_create(db)


@router.get("/", response_model=SettingOut)
def get_setting(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return _get_or_create(db)


LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "logo.png")


@router.post("/logo")
async def upload_logo(
    file: UploadFile = File(...),
    _: Annotated[User, Depends(require_role("admin", "owner"))] = None,
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File harus berupa gambar")
    os.makedirs(os.path.dirname(LOGO_PATH), exist_ok=True)
    with open(LOGO_PATH, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": "Logo berhasil diupload"}


@router.delete("/logo")
def delete_logo(_: Annotated[User, Depends(require_role("admin", "owner"))]):
    if os.path.exists(LOGO_PATH):
        os.remove(LOGO_PATH)
    return {"message": "Logo dihapus"}


@router.get("/printers")
def list_printers(_: Annotated[User, Depends(get_current_user)]) -> dict:
    printers: List[str] = []
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["wmic", "printer", "get", "name"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines():
                name = line.strip()
                if name and name != "Name":
                    printers.append(name)
        else:
            import glob
            printers = sorted(glob.glob("/dev/usb/lp*") + glob.glob("/dev/ttyUSB*"))
    except Exception:
        pass
    return {"printers": printers}


@router.put("/", response_model=SettingOut)
def update_setting(
    payload: SettingUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    setting = _get_or_create(db)
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(setting, k, v)
    db.commit()
    db.refresh(setting)
    return setting
