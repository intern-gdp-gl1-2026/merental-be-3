from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.car import Car


class CarRepository(ABC):
    @abstractmethod
    def save(self, car: Car) -> Car:
        """Save a car to the repository and return the saved car"""
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Car]:
        """Find a car by id, returns None if not found"""
        pass

    @abstractmethod
    def find_all(self) -> list[Car]:
        """Find all cars in the repository"""
        pass

    @abstractmethod
    def find_by_regional_id(self, regional_id: int) -> list[Car]:
        """Find all cars in a specific regional"""
        pass

    @abstractmethod
    def update(self, car: Car) -> Car:
        """Update a car in the repository and return the updated car"""
        pass

    @abstractmethod
    def delete(self, car: Car) -> None:
        """Delete a car from the repository"""
        pass

    @abstractmethod
    def find_by_plate_number(self, plate_number: str) -> Optional[Car]:
        """Find a car by plate number, returns None if not found"""
        pass
