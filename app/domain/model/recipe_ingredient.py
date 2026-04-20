import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredient"

    recipe_id = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("recipe.id"),
        primary_key=True
    )

    ingredient_id = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("ingredient.id"),
        primary_key=True
    )

    amount = sa.Column(sa.Numeric, nullable=False)
    unit = sa.Column(sa.String(20), nullable=False)

    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")
