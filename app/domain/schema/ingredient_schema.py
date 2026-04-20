from pydantic import BaseModel, Field, ConfigDict


class IngredientSchema(BaseModel):
    """"""
    name: str
    amount: float = Field(gt=0)
    unit: str

    model_config = ConfigDict(from_attributes=True)
