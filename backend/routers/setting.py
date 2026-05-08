from typing import Annotated
from fastapi import APIRouter, Depends
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


@router.get("/", response_model=SettingOut)
def get_setting(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return _get_or_create(db)


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
