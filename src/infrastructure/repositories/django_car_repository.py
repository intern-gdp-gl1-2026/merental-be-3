from typing import Optional
import logging

from django.db import DatabaseError

from src.domain.entities.car import Car
from src.domain.repositories.car_repository import CarRepository
from src.infrastructure.models.car_model import CarModel
from src.infrastructure.models.regional_model import RegionalModel


logger = logging.getLogger(__name__)


class DjangoCarRepository(CarRepository):
    def save(self, car: Car) -> Car:
        """Save a car entity to the database

        Args:
            car: Car entity to save

        Returns:
            Car: Saved car entity with ID

        Raises:
            IntegrityError: If plate number already exists (race condition)
            DatabaseError: For other database errors
        """
        try:
            regional = RegionalModel.objects.get(id=car.regional_id)
        except RegionalModel.DoesNotExist:
            raise ValueError(f"Regional with ID {car.regional_id} not found")

        car_model = CarModel(
            name=car.name,
            brand=car.brand,
            model=car.model,
            year=car.year,
            plate_number=car.plate_number,
            color=car.color,
            price_per_day=car.price_per_day,
            regional=regional,
        )
        car_model.save()
        car.id = car_model.id
        return car

    def find_by_id(self, id: int) -> Optional[Car]:
        """Find a car by ID

        Args:
            id: Car ID to search for

        Returns:
            Car entity if found, None otherwise

        Raises:
            DatabaseError: For database errors
        """
        try:
            car_model = CarModel.objects.get(id=id)
            return self._model_to_entity(car_model)
        except CarModel.DoesNotExist:
            return None
        except DatabaseError as e:
            logger.error(f"Database error in find_by_id: {e}")
            raise

    def find_all(self) -> list[Car]:
        """Find all cars in the database

        Returns:
            List of car entities

        Raises:
            DatabaseError: For database errors
        """
        try:
            car_models = CarModel.objects.all()
            return [self._model_to_entity(car_model) for car_model in car_models]
        except DatabaseError as e:
            logger.error(f"Database error in find_all: {e}")
            raise

    def find_by_regional_id(self, regional_id: int) -> list[Car]:
        """Find all cars in a specific regional

        Args:
            regional_id: Regional ID to filter by

        Returns:
            List of car entities in the regional

        Raises:
            DatabaseError: For database errors
        """
        try:
            car_models = CarModel.objects.filter(regional_id=regional_id)
            return [self._model_to_entity(car_model) for car_model in car_models]
        except DatabaseError as e:
            logger.error(f"Database error in find_by_regional_id: {e}")
            raise

    def update(self, car: Car) -> Car:
        """Update a car in the database

        Args:
            car: Car entity with updated values

        Returns:
            Updated car entity

        Raises:
            ValueError: If car not found or regional_id is invalid
            DatabaseError: For other database errors
        """
        if not car.id:
            raise ValueError("Car must have an ID to be updated")

        try:
            car_model = CarModel.objects.get(id=car.id)
        except CarModel.DoesNotExist:
            raise ValueError(f"Car with ID {car.id} not found")

        # Validate regional exists
        try:
            RegionalModel.objects.get(id=car.regional_id)
        except RegionalModel.DoesNotExist:
            raise ValueError(f"Regional with ID {car.regional_id} not found")

        try:
            car_model.name = car.name
            car_model.brand = car.brand
            car_model.model = car.model
            car_model.year = car.year
            car_model.plate_number = car.plate_number
            car_model.color = car.color
            car_model.price_per_day = car.price_per_day
            car_model.regional_id = car.regional_id
            car_model.save()
            return car
        except DatabaseError as e:
            logger.error(f"Database error in update: {e}")
            raise

    def delete(self, car: Car) -> None:
        """Delete a car from the database

        Args:
            car: Car entity to delete

        Raises:
            ValueError: If car not found
            DatabaseError: For other database errors
        """
        if not car.id:
            raise ValueError("Car must have an ID to be deleted")

        try:
            car_model = CarModel.objects.get(id=car.id)
            car_model.delete()
        except CarModel.DoesNotExist:
            raise ValueError(f"Car with ID {car.id} not found")
        except DatabaseError as e:
            logger.error(f"Database error in delete: {e}")
            raise

    def find_by_plate_number(self, plate_number: str) -> Optional[Car]:
        """Find a car by plate number

        Args:
            plate_number: Plate number to search for

        Returns:
            Car entity if found, None otherwise

        Raises:
            DatabaseError: For database errors
        """
        try:
            car_model = CarModel.objects.get(plate_number=plate_number)
            return self._model_to_entity(car_model)
        except CarModel.DoesNotExist:
            return None
        except DatabaseError as e:
            logger.error(f"Database error in find_by_plate_number: {e}")
            raise

    @staticmethod
    def _model_to_entity(car_model: CarModel) -> Car:
        """Convert a CarModel to a Car entity

        Args:
            car_model: Django model instance

        Returns:
            Car entity
        """
        return Car(
            id=car_model.id,
            name=car_model.name,
            brand=car_model.brand,
            model=car_model.model,
            year=car_model.year,
            plate_number=car_model.plate_number,
            color=car_model.color,
            price_per_day=float(car_model.price_per_day),
            regional_id=car_model.regional_id,
        )
