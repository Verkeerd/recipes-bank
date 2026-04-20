from pydantic import BaseModel, Field, field_validator


from app.domain.schema import IngredientSchema


class RecipeRequest(BaseModel):
    """All data necessary to create a new Recipe."""
    name: str = Field(min_length=1, max_length=50)
    description: str | None
    ingredients: list[IngredientSchema]
    steps: list[str]
    vegetarian: bool
    servings: int = Field(gt=0)


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
