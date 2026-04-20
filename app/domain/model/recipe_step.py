import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class RecipeStep(Base):
    """Model for recipe steps. Separating these steps from the recipe enables step by step fetching."""
    __tablename__ = "recipe_step"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, index=True)
    recipe_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("recipe.id"))
    step_number = sa.Column(sa.Integer, nullable=False)
    description = sa.Column(sa.Text, nullable=False)

    recipe = relationship("Recipe", back_populates="steps")
