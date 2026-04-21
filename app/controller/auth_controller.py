from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import get_auth_service
from app.domain.schema.user_request import UserRequest
from app.domain.schema.user_response import UserResponse
from app.service.auth_service import AuthService

from app.domain.schema import Token

auth_router = APIRouter(prefix="/auth", tags=["authentication"])

@auth_router.post(
    "/login",
    response_model=Token,
    summary="Login (JWT authentication)",
    description="""
Authenticate a user using **username and password** and return a JWT access token.

### Flow
- Uses OAuth2 password flow (`application/x-www-form-urlencoded`)
- On success, returns a JWT token
- Token must be included in protected requests:
    Authorization: Bearer <token>
    
### Notes
- Token expires after 60 minutes
- No refresh token mechanism is implemented
""",
    responses={
        200: {"description": "Authentication successful"},
        401: {"description": "Invalid username or password"},
        422: {"description": "Validation error (missing form fields)"},
    },
)
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth: AuthService = Depends(get_auth_service),
):
    """
    Authenticate user and return JWT token.

    Args:
        form_data: OAuth2 form (username + password)
        auth: AuthService dependency

    Returns:
        Token: JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
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


@auth_router.post(
    "/create",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="""
Create a new user account.

- `username`: 3–50 characters, must be unique
- `email`: valid email format, must be unique
- `password`: minimum 8 characters

### Notes
- This endpoint does **not** return a token
- User must login separately after registration
""",
    responses={
        201: {"description": "User successfully created"},
        409: {"description": "Username or email already exists"},
        422: {"description": "Validation error"},
    },
)
def create_user(
    request: UserRequest,
    auth: AuthService = Depends(get_auth_service),
):
    """
    Register a new user.

    Args:
        request: User creation payload
        auth: AuthService dependency

    Returns:
        UserResponse: Created user (without password)

    Raises:
        HTTPException:
            - 409 if username/email already exists
            - 422 if validation fails
    """
    user = auth.add_user(request)
    return user