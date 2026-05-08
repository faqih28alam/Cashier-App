from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from passlib.context import CryptContext

from dependencies import get_db, SECRET_KEY, ALGORITHM
from models.user import User
from schemas.user import LoginRequest, TokenOut, UserOut

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not pwd_context.verify(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username atau password salah")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akun tidak aktif")

    token = jwt.encode(
        {"sub": user.id, "exp": datetime.utcnow() + timedelta(hours=12)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return TokenOut(access_token=token, user=UserOut.model_validate(user))
