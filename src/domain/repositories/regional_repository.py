from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.regional import Regional


class RegionalRepository(ABC):
    @abstractmethod
    def save(self, regional: Regional) -> Regional:
        """Save a regional to the repository and return the saved regional"""
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Regional]:
        """Find a regional by id, returns None if not found"""
        pass

    @abstractmethod
    def find_all(self) -> list[Regional]:
        """Find all regionals in the repository"""
        pass

    @abstractmethod
    def update(self, regional: Regional) -> Regional:
        """Update a regional in the repository and return the updated regional"""
        pass

    @abstractmethod
    def delete(self, regional: Regional) -> None:
        """Delete a regional from the repository"""
        pass
