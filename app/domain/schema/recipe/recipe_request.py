from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.domain.schema import IngredientSchema
from app.domain.schema.step_schema import StepRequest


class RecipeRequest(BaseModel):
    """Schema with data to create a new Recipe with validators."""
    name: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, min_length=1, max_length=256)
    ingredients: list[IngredientSchema]
    steps: list[StepRequest]
    vegetarian: bool
    servings: int = Field(gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Pasta",
                "description": "Simple pasta dish",
                "ingredients": [
                    {"name": "pasta", "amount": 200, "unit": "g"}
                ],
                "steps": [
                    "Boil water",
                    "Cook pasta"
                ],
                "vegetarian": True,
                "servings": 2
            }
        },
        extra="forbid"
    )

    @field_validator("steps", mode="before")
    @classmethod
    def parse_steps(cls, v):
        """
        Accept:
        - list[str]
        - already-valid StepRequest objects
        """
        if not isinstance(v, list):
            raise ValueError("steps must be a list")

        parsed = []
        for i, item in enumerate(v):
            if isinstance(item, str):
                parsed.append(StepRequest(description=item))
            elif isinstance(item, StepRequest):
                parsed.append(item)
            else:
                raise ValueError(f"Invalid step format at index {i}")

        return parsed

    @field_validator("steps")
    @classmethod
    def min_steps(cls, v):
        """A Recipe must have a minimum of one instruction step."""
        if len(v) < 1:
            raise ValueError("Recipe must have at least one step")
        return v

    @field_validator("ingredients")
    @classmethod
    def min_ingredients(cls, v):
        """A Recipe must have a minimum of one ingredient."""
        if len(v) < 1:
            raise ValueError("Recipe must have at least one ingredient.")
        return v
