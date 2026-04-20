import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Recipe(Base):
    """
    Model for Recipes.

    The model contains an id, description, list of ingredients and steps. the id is only used inside
    of the database. Whether a recipe is vegetarian or not is based on the vegetarian status of the ingredients."""
    __tablename__ = "recipe"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = sa.Column(sa.String(50), nullable=False)
    description = sa.Column(sa.String, nullable=True)
    vegetarian = sa.Column(sa.Boolean, nullable=False)
    servings = sa.Column(sa.Integer, nullable=False)

    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    steps = relationship(
        "RecipeStep",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeStep.step_number"
    )
