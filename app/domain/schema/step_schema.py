import uuid

from pydantic import BaseModel, ConfigDict, Field


class StepSchema(BaseModel):
    """"""
    step_number: int
    description: str = Field(max_length=5000)

    model_config = ConfigDict(from_attributes=True)


class StepRequest(BaseModel):
    """"""
    description: str = Field(max_length=5000)

    model_config = ConfigDict(from_attributes=True)
