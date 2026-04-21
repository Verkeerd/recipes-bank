import uuid

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    name: str

    model_config = ConfigDict(from_attributes=True)