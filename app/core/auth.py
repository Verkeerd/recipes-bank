from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.user_repository import UserRepository
from app.service.auth_service import AuthService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(UserRepository(db))


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth: AuthService = Depends(get_auth_service),
):
    user = auth.get_user_from_token(token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_active_user(
    user=Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    return auth.verify_active_user(user)