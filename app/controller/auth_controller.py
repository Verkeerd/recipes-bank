from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import get_auth_service
from app.domain.schema.user_request import UserRequest
from app.domain.schema.user_response import UserResponse
from app.service.auth_service import AuthService

from app.domain.schema import Token

auth_router = APIRouter(prefix="/auth", tags=["authentication"])


@auth_router.post("/login", response_model=Token)
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth: AuthService = Depends(get_auth_service),
):
    user = auth.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_minutes=60
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@auth_router.post("/create", response_model=UserResponse)
def create_user(
    request: UserRequest,
    auth: AuthService = Depends(get_auth_service),
):
    user = auth.add_user(request)
    return user