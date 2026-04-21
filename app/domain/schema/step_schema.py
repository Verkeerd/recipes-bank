import uuid

from pydantic import BaseModel, ConfigDict, Field


class StepSchema(BaseModel):
    """Schema for a recipe step response."""
    step_number: int
    description: str = Field(max_length=5000)

    model_config = ConfigDict(from_attributes=True)


class StepRequest(BaseModel):
    """Schema for a recipe step request with validators."""
    description: str = Field(max_length=5000)

    model_config = ConfigDict(from_attributes=True)
