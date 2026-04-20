from pydantic import BaseModel, ConfigDict

from app.domain.schema import IngredientSchema, StepSchema


class RecipeResponse(BaseModel):
    name: str
    ingredients: list[IngredientSchema]
    steps: list[StepSchema]
    vegetarian: bool
    servings: int

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_recipe(cls, recipe):
        return cls(
            name=recipe.name,
            vegetarian=recipe.vegetarian,
            servings=recipe.servings,
            ingredients=[
                IngredientSchema(
                    name=item.ingredient.name,
                    amount=item.amount,
                    unit=item.unit,
                )
                for item in recipe.recipe_ingredients
            ],
            steps=[
                StepSchema(
                    step_number=s.step_number,
                    description=s.description
                )
                for s in recipe.steps
            ]
        )