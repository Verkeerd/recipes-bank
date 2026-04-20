from sqlalchemy.orm import Session

from app.repository.recipe_repository import RecipeRepository
from app.repository.ingredient_repository import IngredientRepository
from app.repository.user_repository import UserRepository
from app.service.ingredient_service import IngredientService

from app.service.recipe_service import RecipeService
from app.service.auth_service import AuthService


class Services:
    """
    Central dependency container.
    Creates and wires all services in one place.
    """

    def __init__(self, db: Session):
        recipe_repo = RecipeRepository(db)
        ingredient_repo = IngredientRepository(db)
        user_repo = UserRepository(db)

        self.ingredient_service = IngredientService(ingredient_repo)

        self.recipe = RecipeService(recipe_repo, ingredient_repo, ingredient_service=self.ingredient_service)
        self.auth = AuthService(user_repo)