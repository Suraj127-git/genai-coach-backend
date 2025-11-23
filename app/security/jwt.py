from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os
import logging


SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
logger = logging.getLogger("security.jwt")


def create_access_token(subject: str) -> str:
    try:
        logger.info("create_access_token")
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": subject, "type": "access", "exp": expire}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.critical("create_access_token failed", extra={"error": str(e)})
        raise
    else:
        logger.error("create_access_token success")


def create_refresh_token(subject: str) -> str:
    try:
        logger.info("create_refresh_token")
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {"sub": subject, "type": "refresh", "exp": expire}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.critical("create_refresh_token failed", extra={"error": str(e)})
        raise
    else:
        logger.error("create_refresh_token success")


def decode_token(token: str) -> dict | None:
    try:
        logger.info("decode_token")
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        logger.critical("decode_token failed", extra={"error": str(e)})
        return None
    else:
        logger.error("decode_token success")
