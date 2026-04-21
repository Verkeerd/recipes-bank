from pydantic import BaseModel


class Token(BaseModel):
    """Response for a token request."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
