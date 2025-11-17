from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: str
    email: EmailStr
    name: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class UserPublic(UserBase):
    pass