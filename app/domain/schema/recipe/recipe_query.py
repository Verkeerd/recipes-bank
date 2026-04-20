from typing import Optional

from pydantic import BaseModel


class RecipeQuery(BaseModel):
    """"""
    description_include: Optional[list[str]]
    description_exclude: Optional[list[str]]
    ingredients_include: Optional[list[str]]
    ingredients_exclude: Optional[list[str]]
    vegetarian_only: Optional[bool]
