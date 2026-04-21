import uuid

from app.domain.model import Ingredient, RecipeIngredient
from app.repository.ingredient_repository import IngredientRepository


class IngredientService:
    def __init__(self, ingredient_repo: IngredientRepository):
        self.ingredient_repo = ingredient_repo

    def add_ingredients(self, ingredients):
        recipe_ingredients = list()
        for item in ingredients:
            ingredient_name = item.name.lower()
            ingredient = self.ingredient_repo.get_by_name(ingredient_name)

            if not ingredient:
                ingredient = Ingredient(name=ingredient_name, uuid=uuid.uuid4())
                self.ingredient_repo.add(ingredient)

            recipe_ingredients.append(
                RecipeIngredient(
                    ingredient=ingredient,
                    amount=item.amount,
                    unit=item.unit
                )
            )

        return recipe_ingredients