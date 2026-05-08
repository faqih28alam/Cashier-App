from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    nama: str
    role: str = "kasir"


class UserUpdate(BaseModel):
    nama: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    nama: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
