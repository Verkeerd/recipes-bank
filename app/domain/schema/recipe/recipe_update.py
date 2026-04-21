from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.domain.schema import IngredientSchema
from app.domain.schema.step_schema import StepRequest


class RecipeUpdate(BaseModel):
    """Schema with information to update a recipe with validators."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, min_length=1, max_length=256)
    ingredients: Optional[list[IngredientSchema]] = None
    steps: Optional[list[StepRequest]] = None
    vegetarian: Optional[bool] = None
    servings: Optional[int] = Field(default=None, gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Pasta",
                "description": "Simple pasta recipe.",
                "ingredients": [
                    {
                        "name": "pasta",
                        "amount": 250,
                        "unit": "g"
                    }
                ],
                "steps": [
                    "Boil salted water",
                    "Cook pasta al dente"
                ],
                "vegetarian": True,
                "servings": 4
            }
        },
        extra="forbid",
    )

    @field_validator("steps", mode="before")
    @classmethod
    def parse_steps(cls, v):
        """
        Accept:
        - null/none
        - list[str]
        - already-valid StepRequest objects
        """
        if v is None:
            return None

        if not isinstance(v, list):
            raise ValueError("steps must be a list")

        return [
            StepRequest(description=item) if isinstance(item, str) else item
            for item in v
        ]
