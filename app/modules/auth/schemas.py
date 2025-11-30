from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    id: str
    email: EmailStr
    name: str | None = None

class UserPublic(UserBase):
    pass

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AuthResponse(BaseModel):
    user: UserPublic
    token: str
    refresh_token: str | None = None

class RefreshRequest(BaseModel):
    refresh_token: str

