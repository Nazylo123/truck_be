"""Declarative Base shared by all SQLAlchemy models.

Models import `Base` from here; Alembic's env.py reads `Base.metadata` for
autogenerate migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Single declarative base cho toàn bộ models trong app."""

    pass