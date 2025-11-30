from passlib.context import CryptContext
import uuid
from .models import User
from .schemas import UserPublic
from ...core.security import create_access_token, create_refresh_token

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def make_user(email: str, name: str | None, password: str) -> User:
    return User(id=str(uuid.uuid4()), email=email, name=name, password_hash=hash_password(password))

def public(user: User) -> UserPublic:
    return UserPublic(id=user.id, email=user.email, name=user.name)

