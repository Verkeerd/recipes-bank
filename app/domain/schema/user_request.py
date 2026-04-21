from pydantic import Field, EmailStr, BaseModel


class UserRequest(BaseModel):
    """Schema with data to create a new user with validators."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=50)