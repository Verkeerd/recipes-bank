from app.core.database import SessionLocal
from app.repository.recipe_repository import RecipeRepository
from app.repository.ingredient_repository import IngredientRepository
from app.service.recipe_service import RecipeService
from app.service.ingredient_service import IngredientService
from app.domain.schema import RecipeRequest, StepRequest


def seed_db():
    db = SessionLocal()

    try:
        ingredient_service = IngredientService(
            IngredientRepository(db)
        )

        recipe_service = RecipeService(
            RecipeRepository(db),
            ingredient_service
        )

        userService

        pancakes = RecipeRequest(
            name="Fluffy Pancakes",
            description="Soft homemade pancakes",
            vegetarian=True,
            servings=4,
            ingredients=[
                {"name": "Flour", "amount": 500, "unit": "gram"},
                {"name": "Egg", "amount": 3, "unit": "pieces"},
                {"name": "Milk", "amount": 400, "unit": "milliliter"},
            ],
            steps=[
                StepRequest(description="Mix ingredients"),
                StepRequest(description="Heat pan"),
                StepRequest(description="Cook until golden"),
            ],
        )

        omelette = RecipeRequest(
            name="Omelette",
            description="Quick egg omelette",
            vegetarian=True,
            servings=1,
            ingredients=[
                {"name": "Egg", "amount": 2, "unit": "pieces"},
                {"name": "Butter", "amount": 20, "unit": "gram"},
            ],
            steps=[
                StepRequest(description="Beat eggs"),
                StepRequest(description="Cook in pan"),
            ],
        )

        smoothie = RecipeRequest(
            name="Banana Smoothie",
            description="Healthy smoothie",
            vegetarian=True,
            servings=1,
            ingredients=[
                {"name": "Banana", "amount": 2, "unit": "pieces"},
                {"name": "Milk", "amount": 150, "unit": "milliliter"},
            ],
            steps=[
                StepRequest(description="Add ingredients"),
                StepRequest(description="Blend"),
            ],
        )

        recipe_service.create_recipe(pancakes)
        recipe_service.create_recipe(omelette)
        recipe_service.create_recipe(smoothie)

        print("🌱 Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print("🍂 Seed failed:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_db()