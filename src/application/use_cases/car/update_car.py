"""Use case for updating a car."""

from src.domain.entities.car import Car
from src.domain.repositories.car_repository import CarRepository


class UpdateCarUseCase:
    """Update an existing car.

    Supports partial updates - only provided fields are updated.
    Regional existence validation is delegated to the repository layer.
    """

    def __init__(self, cars: CarRepository, regionals=None):
        self.cars = cars
        # regionals parameter kept for backward compatibility but not used

    def execute(self, car_id: int, **update_fields) -> Car:
        """Update a car.

        Args:
            car_id: The car ID to update
            **update_fields: Fields to update (e.g., color="Black")

        Returns:
            The updated car

        Raises:
            ValueError: If car not found, regional doesn't exist, or plate number already exists
            DomainValidationError: If updated data is invalid
        """
        # Get existing car
        car = self.cars.find_by_id(car_id)
        if not car:
            raise ValueError(f"Car with ID {car_id} not found")

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

        # Save to repository (regional validation happens in repository layer)
        return self.cars.update(car)
