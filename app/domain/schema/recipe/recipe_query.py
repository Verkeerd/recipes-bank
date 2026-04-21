from typing import Optional

from pydantic import BaseModel, ConfigDict


class RecipeQuery(BaseModel):
    """Schema containing all data a recipe can be queried with. """
    description_include: Optional[list[str]]
    description_exclude: Optional[list[str]]
    ingredients_include: Optional[list[str]]
    ingredients_exclude: Optional[list[str]]
    vegetarian: Optional[bool]
    servings: Optional[int]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description_include": [
                    "Cook"
                ],
                "description_exclude": [
                    "Simple"
                ],
                "ingredients_include": [
                    "Pasta"
                ],
                "ingredients_exclude": [
                    "Pork",
                    "Beef"
                ],
                "vegetarian": True,
                "servings": 2
            }
        },
        extra="forbid"
    )
