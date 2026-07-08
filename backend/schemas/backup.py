from typing import Optional
from pydantic import BaseModel


class BackupLoginRequest(BaseModel):
    client_id: str
    password: str


class BackupChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class BackupStatusOut(BaseModel):
    connected: bool
    client_id: Optional[str] = None


class BackupFileInfo(BaseModel):
    filename: str
    size: int
    created_at: str
