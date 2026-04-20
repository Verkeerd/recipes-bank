import uuid
from sqlalchemy.orm import Session, joinedload
from app.domain.model import Recipe


class RecipeRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, recipe: Recipe):
        self.db.add(recipe)

    def get_all(self):
        return self.db.query(Recipe).options(
            joinedload(Recipe.recipe_ingredients),
            joinedload(Recipe.steps)
        ).all()

    def get_by_id(self, recipe_id: uuid.UUID):
        return self.db.query(Recipe).options(
            joinedload(Recipe.recipe_ingredients),
            joinedload(Recipe.steps)
        ).filter(Recipe.id == recipe_id).first()

    def delete(self, recipe: Recipe):
        self.db.delete(recipe)

    def refresh(self, entity):
        self.db.refresh(entity)
        return entity
