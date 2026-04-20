import uuid


from app.domain.model import RecipeStep, Recipe
from app.domain.schema import RecipeRequest, RecipeUpdate
from app.domain.schema.recipe import recipe_query
from app.repository.recipe_repository import RecipeRepository
from app.service.ingredient_service import IngredientService


class RecipeService:

    def __init__(self, recipe_repo: RecipeRepository, ingredient_service : IngredientService):
        self.recipe_repo = recipe_repo
        self.ingredient_service = ingredient_service

    def create_recipe(self, data: RecipeRequest):
        """Creates a new recipe.

        Checks if ingredients are registered in the database and registers them if not. Adds the ingredient with
        the amount and unit of measurement to the recipe. Numbers the instuction steps and adds them to the recipe.
        Persists the recipe to the database."""
        recipe = Recipe(
            id=uuid.uuid4(),
            name=data.name,
            description=data.description,
            vegetarian=data.vegetarian,
            servings=data.servings
        )

        recipe.recipe_ingredients = self.ingredient_service.add_ingredients(data.ingredients)

        recipe.steps = self.number_recipe_steps(data.steps)

        self.recipe_repo.add(recipe)
        self.recipe_repo.db.commit()
        return self.recipe_repo.refresh(recipe)


    def number_recipe_steps(self, steps):
        return [
            RecipeStep(
                id=uuid.uuid4(),
                step_number=i + 1,
                description=step.description,
            )
            for i, step in enumerate(steps)
        ]

    def update_recipe(self, recipe_id: uuid.UUID, data: RecipeUpdate):
        recipe = self.recipe_repo.get_by_id(recipe_id)

        if not recipe:
            return None

        if isinstance(data.name, str):
            recipe.name = data.name

        if isinstance(data.description, str):
            recipe.description = data.description

        if isinstance(data.ingredients, list):
            recipe.recipe_ingredients = self.ingredient_service.add_ingredients(data.ingredients)

        if isinstance(data.steps, list):
            recipe.steps = self.number_recipe_steps(data.steps)

        if isinstance(data.vegetarian, bool):
            recipe.vegetarian = data.vegetarian

        if isinstance(data.servings, int):
            recipe.servings = data.servings

        self.recipe_repo.db.commit()
        return self.recipe_repo.refresh(recipe)

    def get_all_recipes(self):
        return self.recipe_repo.get_all()

    def get_recipe(self, recipe_id: uuid.UUID):
        return self.recipe_repo.get_by_id(recipe_id)

    def delete_recipe(self, recipe_id: uuid.UUID):
        recipe = self.recipe_repo.get_by_id(recipe_id)

        if not recipe:
            return False

        self.recipe_repo.delete(recipe)
        self.recipe_repo.db.commit()

        return True

    def query_recipe(self, request: recipe_query.RecipeQuery):
        return self.recipe_repo.build_query(request).all()
