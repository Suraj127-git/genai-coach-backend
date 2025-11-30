from sqlalchemy.orm import Session
from .models import User

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

