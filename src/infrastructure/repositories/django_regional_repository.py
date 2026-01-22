from typing import Optional
import logging

from django.db import DatabaseError

from src.domain.entities.regional import Regional
from src.domain.repositories.regional_repository import RegionalRepository
from src.infrastructure.models.regional_model import RegionalModel


logger = logging.getLogger(__name__)


class DjangoRegionalRepository(RegionalRepository):
    def save(self, regional: Regional) -> Regional:
        """Save a regional entity to the database

        Args:
            regional: Regional entity to save

        Returns:
            Regional: Saved regional entity with ID

        Raises:
            IntegrityError: If a regional with the same name already exists (race condition)
            DatabaseError: For other database errors
        """
        regional_model = RegionalModel(name=regional.name)
        regional_model.save()
        regional.id = regional_model.id
        return regional

    def find_by_id(self, id: int) -> Optional[Regional]:
        """Find a regional by id (case-insensitive)

        Args:
            id: id to search for

        Returns:
            Regional entity if found, None otherwise
        """
        try:
            # Use iexact for case-insensitive lookup
            regional_model = RegionalModel.objects.get(id=id)
            return Regional(
                id=regional_model.id,
                name=regional_model.name,
            )
        except RegionalModel.DoesNotExist:
            return None
        except DatabaseError as e:
            # Log database errors for debugging while returning None to prevent exposure
            logger.error(f"Database error in find_by_id: {e}")
            return None

    def find_all(self) -> list[Regional]:
        """Find all regionals in the repository"""
        regional_models = RegionalModel.objects.all()
        return [
            Regional(id=regional_model.id, name=regional_model.name)
            for regional_model in regional_models
        ]

    def update(self, regional: Regional) -> Regional:
        """Update a regional entity in the database"""
        regional_model = RegionalModel.objects.get(id=regional.id)
        regional_model.name = regional.name
        regional_model.save()
        return regional

    def delete(self, regional: Regional) -> None:
        """Delete a regional entity from the database"""
        regional_model = RegionalModel.objects.get(id=regional.id)
        regional_model.delete()
