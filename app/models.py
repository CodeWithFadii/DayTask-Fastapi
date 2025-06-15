import uuid
from sqlalchemy import ARRAY, UUID, Column, Integer, String, DateTime, text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )

    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=True)
    name = Column(String, nullable=False)

    profile_img = Column(String, nullable=True)
    user_type = Column(String, nullable=True, server_default="email", default=[])

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    owner_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    details = Column(String, nullable=False)
    team_members = Column(ARRAY(String), nullable=True)
    time = Column(String, nullable=False)
    date = Column(String, nullable=False)
    is_completed = Column(Boolean, nullable=True, default=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
