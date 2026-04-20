import uuid
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.domain.model import Ingredient, Recipe, RecipeStep, User, Account, RecipeIngredient


def seed_db():
    """Seeds a user, three ingredients and a recipe with three ingredients and three steps."""
    db: Session = SessionLocal()

    try:
        user1 = User(
            id=uuid.uuid4(),
            username="piet",
            email="piet@heijn.com",
            name="Piet Heijn",
            active=True,
        )

        account1 = Account(
            id=user1.id,
            password="hashed_password_here"
        )

        user1._account = account1

        flour = Ingredient(
            id=uuid.uuid4(),
            name="Flour",
        )

        egg = Ingredient(
            id=uuid.uuid4(),
            name="Egg",
        )

        milk = Ingredient(
            id=uuid.uuid4(),
            name="Milk",
        )

        pancake = Recipe(
            id=uuid.uuid4(),
            name="Fluffy Pancakes",
            description="Fluffy homemade pancakes",
            vegetarian=True,
            servings=6
        )

        ingredient1 = RecipeIngredient(
            ingredient=flour,
            recipe=pancake,
            amount=500,
            unit="gram"
        )

        ingredient2 = RecipeIngredient(
            ingredient=egg,
            recipe=pancake,
            amount=3,
            unit="pieces"
        )

        ingredient3 = RecipeIngredient(
            ingredient=milk,
            recipe=pancake,
            amount=400,
            unit="milliliter"
        )

        step1 = RecipeStep(
            id=uuid.uuid4(),
            step_number=1,
            description="Mix flour, eggs, and milk",
            recipe=pancake,
        )

        step2 = RecipeStep(
            id=uuid.uuid4(),
            step_number=2,
            description="Heat pan and cook batter",
            recipe=pancake,
        )

        pancake.recipe_ingredients = [ingredient1, ingredient2, ingredient3]

        db.add(user1)
        db.add_all([flour, egg, milk])
        db.add_all([ingredient1, ingredient2, ingredient3])
        db.add(pancake)
        db.add_all([step1, step2])

        db.commit()

        print("🌱 Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print("🍂 Seed failed:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_db()