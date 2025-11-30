from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
import logging
from ...core.dependencies import get_db, get_current_user_id
from ...core.security import create_access_token, create_refresh_token, decode_token
from .repository import AuthRepository
from .service import verify_password, make_user, public
from .schemas import UserCreate, UserPublic, LoginRequest, AuthResponse, TokenPair, RefreshRequest

router = APIRouter()
logger = logging.getLogger("auth")

@router.post("/register", response_model=AuthResponse)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    existing = repo.by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = make_user(payload.email, payload.name, payload.password)
    repo.save(user)
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    response.set_cookie(key="refresh_token", value=refresh, httponly=True, secure=False, samesite="lax", path="/")
    return AuthResponse(user=public(user), token=access, refresh_token=refresh)

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    user = repo.by_email(payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    response.set_cookie(key="refresh_token", value=refresh, httponly=True, secure=False, samesite="lax", path="/")
    return AuthResponse(user=public(user), token=access, refresh_token=refresh)

@router.get("/me", response_model=UserPublic)
def me(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    user = repo.by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return public(user)

@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest | None = None, response: Response = None, refresh_token: str | None = Cookie(default=None)):
    try:
        logger.info("refresh token request")
        token = payload.refresh_token if payload and payload.refresh_token else refresh_token
        data = decode_token(token) if token else None
        if not data or data.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        sub = data.get("sub")
        new_access = create_access_token(sub)
        new_refresh = create_refresh_token(sub)
        response.set_cookie(key="refresh_token", value=new_refresh, httponly=True, secure=False, samesite="lax", path="/")
        return TokenPair(access_token=new_access, refresh_token=new_refresh)
    except HTTPException as e:
        logger.critical("refresh failed", extra={"error": str(e)})
        raise
    else:
        logger.error("refresh success")

@router.put("/me")
def update_me(payload: dict, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    user = repo.by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_email = payload.get("email")
    new_name = payload.get("name")
    current_password = payload.get("currentPassword")
    new_password = payload.get("newPassword")
    if new_email and new_email != user.email:
        if repo.by_email(new_email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        user.email = new_email
    if new_name is not None:
        user.name = new_name
    if new_password:
        from .service import verify_password as vp, hash_password
        if not current_password or not vp(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password invalid")
        user.password_hash = hash_password(new_password)
    repo.save(user)
    return {"user": public(user)}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token", path="/")
    return {"ok": True}

