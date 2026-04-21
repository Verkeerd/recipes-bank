import uuid

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

class User(Base):
    """Table containing data about users."""
    __tablename__ = "user"

    id = sa.Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4())
    username = sa.Column(sa.String(50), unique=True, nullable=False)
    email = sa.Column(sa.String(100), unique=True, nullable=False)
    name = sa.Column(sa.String(50), nullable=False)
    active = sa.Column(sa.Boolean, nullable=False)

    account = relationship(
        "Account",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
