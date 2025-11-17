from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    user: "UserPublic"
    token: str
    refresh_token: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


from .user import UserPublic  # noqa: E402