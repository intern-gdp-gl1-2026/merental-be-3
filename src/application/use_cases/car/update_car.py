"""Use case for updating a car."""

from src.domain.entities.car import Car
from src.domain.repositories.car_repository import CarRepository
from src.domain.repositories.regional_repository import RegionalRepository


class UpdateCarUseCase:
    """Update an existing car.

    Supports partial updates - only provided fields are updated.
    """

    def __init__(self, cars: CarRepository, regionals: RegionalRepository):
        self.cars = cars
        self.regionals = regionals

    def execute(self, car_id: int, **update_fields) -> Car:
        """Update a car.

        Args:
            car_id: The car ID to update
            **update_fields: Fields to update (e.g., color="Black")

        Returns:
            The updated car

        Raises:
            ValueError: If car not found
            DomainValidationError: If updated data is invalid
        """
        # Get existing car
        car = self.cars.find_by_id(car_id)
        if not car:
            raise ValueError(f"Car with ID {car_id} not found")

        # If regional_id is being updated, validate it exists
        if "regional_id" in update_fields:
            regional_id = update_fields["regional_id"]
            regional = self.regionals.find_by_id(regional_id)
            if not regional:
                raise ValueError(f"Regional with ID {regional_id} not found")

        # If plate number is being updated, check uniqueness
        if (
            "plate_number" in update_fields
            and update_fields["plate_number"] != car.plate_number
        ):
            existing_car = self.cars.find_by_plate_number(update_fields["plate_number"])
            if existing_car:
                raise ValueError(
                    f"Car with plate number {update_fields['plate_number']} already exists"
                )

        # Update car with validation
        car.update(**update_fields)

        # Save to repository
        return self.cars.update(car)
