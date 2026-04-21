import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from passlib.context import CryptContext
import jwt
from sqlalchemy.exc import IntegrityError

from app.domain.model import User, Account
from app.domain.schema.user_request import UserRequest


class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo
        self.secret_key = os.getenv("SECRET_AUTH_KEY")
        self.algorithm = "HS256"
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        if not self.secret_key:
            raise RuntimeError("SECRET_AUTH_KEY is missing")

    from sqlalchemy.exc import IntegrityError
    from fastapi import HTTPException

    def add_user(self, data: UserRequest) -> User:
        user = User(
            id=uuid.uuid4(),
            name=data.name,
            email=data.email,
            username=data.username,
            active=True
        )

        account = Account(
            id=uuid.uuid4(),
            password=self.encrypt_password(data.password)
        )

        user.account = account

        try:
            return self.user_repo.save(user)

        except IntegrityError as e:
            self.user_repo.db.rollback()

            error_msg = str(e.orig)

            if "user_email_key" in error_msg:
                raise HTTPException(
                    status_code=409,
                    detail="Email is already in use."
                )

            if "user_username_key" in error_msg:
                raise HTTPException(
                    status_code=409,
                    detail="Username already exists"
                )

            raise HTTPException(
                status_code=500,
                detail=f"Database error: {e}"
            )

    def encrypt_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        return self.pwd_context.verify(password, hashed)

    def authenticate_user(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)

        if not user or not user.account:
            return None

        if not self.verify_password(password, user.account.password):
            return None

        return user

    def create_access_token(self, data: dict, expires_minutes: int = 60) -> str:
        payload = data.copy()

        payload["sub"] = data.get("sub") or data.get("username")
        payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def get_user_from_token(self, token: str) -> User | None:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )

            username = payload.get("sub")

            if not username:
                return None

            return self.user_repo.get_by_username(username)

        except jwt.ExpiredSignatureError:
            return None

        except jwt.InvalidTokenError:
            return None