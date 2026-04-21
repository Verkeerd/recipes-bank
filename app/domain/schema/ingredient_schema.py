from pydantic import BaseModel, Field, ConfigDict


class IngredientSchema(BaseModel):
    """Schema for an ingredient response."""
    name: str = Field(max_length=50)
    amount: float = Field(gt=0)
    unit: str = Field(max_length=50)

    model_config = ConfigDict(from_attributes=True)
