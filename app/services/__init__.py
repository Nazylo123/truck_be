"""Service layer — business logic, orchestration, validation.

Tách khỏi router (controller) và repository (data access).
"""

from app.services.truck_service import TruckService

__all__ = ["TruckService"]