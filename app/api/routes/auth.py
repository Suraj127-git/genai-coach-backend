from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import uuid

from ...db.models import User
from ...db.session import SessionLocal
from ...schemas.user import UserCreate, UserPublic
from ...schemas.auth import LoginRequest, AuthResponse, TokenPair, RefreshRequest
from ...security.jwt import create_access_token, create_refresh_token, decode_token
from ..deps import get_db, get_current_user_id


pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/register", response_model=AuthResponse)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )
    return AuthResponse(user=UserPublic(id=user.id, email=user.email, name=user.name), token=access, refresh_token=refresh)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )
    return AuthResponse(user=UserPublic(id=user.id, email=user.email, name=user.name), token=access, refresh_token=refresh)


@router.get("/me", response_model=UserPublic)
def me(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserPublic(id=user.id, email=user.email, name=user.name)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest | None = None, response: Response = None, refresh_token: str | None = Cookie(default=None)):
    token = None
    if payload and payload.refresh_token:
        token = payload.refresh_token
    elif refresh_token:
        token = refresh_token
    data = decode_token(token) if token else None
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    sub = data.get("sub")
    new_access = create_access_token(sub)
    new_refresh = create_refresh_token(sub)
    if response is not None:
        response.set_cookie(
            key="refresh_token",
            value=new_refresh,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
        )
    return TokenPair(access_token=new_access, refresh_token=new_refresh)


@router.put("/me")
def update_me(
    payload: dict,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_email: Optional[str] = payload.get("email")
    new_name: Optional[str] = payload.get("name")
    current_password: Optional[str] = payload.get("currentPassword")
    new_password: Optional[str] = payload.get("newPassword")

    if new_email and new_email != user.email:
        exists = db.query(User).filter(User.email == new_email).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        user.email = new_email

    if new_name is not None:
        user.name = new_name

    if new_password:
        if not current_password or not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password invalid")
        user.password_hash = hash_password(new_password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"user": UserPublic(id=user.id, email=user.email, name=user.name)}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token", path="/")
    return {"ok": True}
