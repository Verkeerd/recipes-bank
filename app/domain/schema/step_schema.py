import uuid

from pydantic import BaseModel, ConfigDict, Field


class StepSchema(BaseModel):
    """"""
    step_number: int
    description: str

    model_config = ConfigDict(from_attributes=True)
