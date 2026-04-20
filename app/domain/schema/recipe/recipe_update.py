from typing import Optional

from pydantic import BaseModel, Field

from app.domain.schema import IngredientSchema, StepSchema


class RecipeUpdate(BaseModel):
    """"""
    name: Optional[str] = Field(min_length=1, max_length=50)
    ingredients: Optional[list[IngredientSchema]]
    steps: Optional[list[str]]
    vegetarian: Optional[bool]
    servings: Optional[int] = Field(gt=0)

