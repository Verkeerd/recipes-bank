import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Account(Base):
    """Table containing sensitive login data. Only used for authentication."""
    __tablename__ = "account"

    id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("user.id"), primary_key=True)
    password = sa.Column(sa.String, nullable=False)

    user = relationship(
        "User",
        back_populates="account"
    )
