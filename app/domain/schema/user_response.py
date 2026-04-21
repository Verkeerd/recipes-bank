import uuid

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    """Schema for a user response."""
    id: uuid.UUID
    username: str
    email: str
    name: str

    model_config = ConfigDict(from_attributes=True)