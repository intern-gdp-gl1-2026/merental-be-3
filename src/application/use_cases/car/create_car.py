"""Use case for creating a new car."""

from src.domain.entities.car import Car
from src.domain.repositories.car_repository import CarRepository
from src.domain.repositories.regional_repository import RegionalRepository


class CreateCarUseCase:
    """Create a new car in the system.

    This use case handles the creation of a new car with validation of:
    - Car data validity (domain validation)
    - Regional existence (foreign key constraint)
    - Plate number uniqueness
    """

    def __init__(self, cars: CarRepository, regionals: RegionalRepository):
        self.cars = cars
        self.regionals = regionals

    def execute(
        self,
        name: str,
        brand: str,
        model: str,
        year: int,
        plate_number: str,
        color: str,
        price_per_day: float,
        regional_id: int,
    ) -> Car:
        """Create a new car.

        Args:
            name: Car name
            brand: Car brand
            model: Car model
            year: Manufacturing year
            plate_number: License plate number
            color: Car color
            price_per_day: Daily rental price
            regional_id: Regional ID

        Returns:
            The created car

        Raises:
            DomainValidationError: If car data is invalid
            ValueError: If regional doesn't exist or plate number already exists
        """
        # Validate regional exists
        regional = self.regionals.find_by_id(regional_id)
        if not regional:
            raise ValueError(f"Regional with ID {regional_id} not found")

        # Check plate number uniqueness
        existing_car = self.cars.find_by_plate_number(plate_number)
        if existing_car:
            raise ValueError(f"Car with plate number {plate_number} already exists")

        # Create and validate car entity
        car = Car(
            name=name,
            brand=brand,
            model=model,
            year=year,
            plate_number=plate_number,
            color=color,
            price_per_day=price_per_day,
            regional_id=regional_id,
        )

        # Save to repository
        return self.cars.save(car)
