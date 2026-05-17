from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from dependencies import get_db, get_current_user, require_role
from models.barang import Barang
from models.kategori import Kategori
from models.supplier import Supplier
from models.user import User
from schemas.barang import BarangCreate, BarangOut, BarangUpdate
from schemas.master import KategoriCreate, KategoriOut, SupplierCreate, SupplierOut
from schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Barang ────────────────────────────────────────────────────────────────────

@router.get("/barang", response_model=list[BarangOut])
def list_barang(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    q: str = Query(default=""),
    kategori_id: Optional[int] = None,
):
    query = db.query(Barang)
    if q:
        query = query.filter(
            Barang.nama_barang.ilike(f"%{q}%") | Barang.barcode.ilike(f"%{q}%")
        )
    if kategori_id:
        query = query.filter(Barang.id_kategori == kategori_id)
    return query.order_by(Barang.nama_barang).all()


@router.get("/barang/{barcode}", response_model=BarangOut)
def get_barang(
    barcode: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    barang = db.get(Barang, barcode)
    if not barang:
        raise HTTPException(status_code=404, detail="Barang tidak ditemukan")
    return barang


@router.post("/barang", response_model=BarangOut)
def create_barang(
    payload: BarangCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    barang = Barang(**payload.model_dump())
    db.add(barang)
    db.commit()
    db.refresh(barang)
    return barang


@router.put("/barang/{barcode}", response_model=BarangOut)
def update_barang(
    barcode: str,
    payload: BarangUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    barang = db.get(Barang, barcode)
    if not barang:
        raise HTTPException(status_code=404, detail="Barang tidak ditemukan")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(barang, k, v)
    db.commit()
    db.refresh(barang)
    return barang


@router.delete("/barang", status_code=204)
def delete_barang(
    barcode: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    barang = db.get(Barang, barcode)
    if not barang:
        raise HTTPException(status_code=404, detail="Barang tidak ditemukan")
    db.delete(barang)
    db.commit()

# ── Kategori ──────────────────────────────────────────────────────────────────

@router.get("/kategori", response_model=list[KategoriOut])
def list_kategori(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Kategori).order_by(Kategori.nama_kategori).all()


@router.post("/kategori", response_model=KategoriOut)
def create_kategori(
    payload: KategoriCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    obj = Kategori(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/kategori/{id}", status_code=204)
def delete_kategori(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    obj = db.get(Kategori, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    db.delete(obj)
    db.commit()

# ── Supplier ──────────────────────────────────────────────────────────────────

@router.get("/supplier", response_model=list[SupplierOut])
def list_supplier(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]):
    return db.query(Supplier).order_by(Supplier.nama_supplier).all()


@router.post("/supplier", response_model=SupplierOut)
def create_supplier(
    payload: SupplierCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    obj = Supplier(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/supplier/{id}", status_code=204)
def delete_supplier(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    obj = db.get(Supplier, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Supplier tidak ditemukan")
    db.delete(obj)
    db.commit()

# ── User ──────────────────────────────────────────────────────────────────────

@router.get("/user", response_model=list[UserOut])
def list_user(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_role("admin", "owner"))]):
    return db.query(User).all()


@router.post("/user", response_model=UserOut)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    hashed = pwd_context.hash(payload.password)
    user = User(**payload.model_dump(exclude={"password"}), password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/user/{id}", response_model=UserOut)
def update_user(
    id: int,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_role("admin", "owner"))],
):
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    data = payload.model_dump(exclude_none=True)
    if "password" in data:
        data["password"] = pwd_context.hash(data["password"])
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/user/{id}", status_code=204)
def delete_user(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("admin", "owner"))],
):
    if id == current_user.id:
        raise HTTPException(status_code=400, detail="Tidak bisa menghapus akun sendiri")
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    db.delete(user)
    db.commit()
