from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.domain.model.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int):
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_username(self, username: str):
        return (
            self.db.query(User).options(
                joinedload(User.account)
            )
            .filter(User.username == username)
            .first()
        )

    def save(self, user: User):
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user

        except IntegrityError as e:
            self.db.rollback()
            raise e
