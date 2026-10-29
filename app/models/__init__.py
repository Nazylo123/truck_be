"""SQLAlchemy ORM models.

Import mọi model module ở đây để chúng được đăng ký vào Base.metadata trước khi
Alembic autogenerate scan. Thêm model mới? Thêm import.
"""

from app.models.truck import Truck  # noqa: F401

__all__ = ["Truck"]