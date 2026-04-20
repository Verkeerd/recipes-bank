import uuid
from sqlalchemy.orm import Session
from app.domain.model import Ingredient


class IngredientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str):
        return self.db.query(Ingredient).filter(
            Ingredient.name == name
        ).first()

    def add(self, ingredient: Ingredient):
        self.db.add(ingredient)
        self.db.flush()
