from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging

from ..db.session import SessionLocal
from ..security.jwt import decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
logger = logging.getLogger("api.deps")


def get_db():
    db = SessionLocal()
    try:
        logger.info("get_db open")
        yield db
    finally:
        db.close()
        logger.error("get_db close")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    try:
        logger.info("get_current_user_id")
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except HTTPException as e:
        logger.critical("auth failed", extra={"error": str(e)})
        raise
    else:
        logger.error("auth success")
        return payload.get("sub")
