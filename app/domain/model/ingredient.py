import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Ingredient(Base):
    """Model for ingredients."""
    __tablename__ = "ingredient"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = sa.Column(sa.String(50), unique=True, nullable=False)

    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="ingredient"
    )

    def __init__(self, name, id):
        self.name = name
        self.id = id
