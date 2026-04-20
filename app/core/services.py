from app.service.recipe_service import RecipeService
from app.service.ingredient_service import IngredientService
from app.service.auth_service import AuthService


class Services:
    def __init__(
        self,
        recipe: RecipeService,
        ingredient: IngredientService,
        auth: AuthService,
    ):
        self.recipe = recipe
        self.ingredient = ingredient
        self.auth = auth