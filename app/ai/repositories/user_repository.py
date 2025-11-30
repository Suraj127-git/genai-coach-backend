from sqlalchemy.orm import Session
from ...db.models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def update(self, user_id: str, name: str | None = None, email: str | None = None) -> User | None:
        u = self.get(user_id)
        if not u:
            return None
        if name is not None:
            u.name = name
        if email is not None:
            u.email = email
        self.db.add(u)
        self.db.commit()
        self.db.refresh(u)
        return u
