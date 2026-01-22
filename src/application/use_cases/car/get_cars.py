"""Use case for retrieving cars."""

from src.domain.entities.car import Car
from src.domain.repositories.car_repository import CarRepository


class GetCarByIdUseCase:
    """Get a single car by ID."""

    def __init__(self, cars: CarRepository):
        self.cars = cars

    def execute(self, car_id: int) -> Car:
        """Get a car by ID.

        Args:
            car_id: The car ID

        Returns:
            The car

        Raises:
            ValueError: If car not found
        """
        car = self.cars.find_by_id(car_id)
        if not car:
            raise ValueError(f"Car with ID {car_id} not found")
        return car


class GetCarsUseCase:
    """Get all cars, optionally filtered by region and date range."""

    def __init__(self, cars: CarRepository):
        self.cars = cars

    def execute(
        self,
        regional_id: int = None,
        start_date: int = None,
        end_date: int = None,
    ) -> list[Car]:
        """Get cars with optional filtering.

        Args:
            regional_id: Filter by regional ID (optional)
            start_date: Start date as Unix timestamp (optional, must be provided with regional_id and end_date)
            end_date: End date as Unix timestamp (optional, must be provided with regional_id and start_date)

        Returns:
            List of cars

        Raises:
            ValueError: If filter parameters are invalid
        """
        # Validate filter parameters
        has_regional = regional_id is not None
        has_start = start_date is not None
        has_end = end_date is not None

        # All three must be provided together or none
        if (has_regional or has_start or has_end) and not (
            has_regional and has_start and has_end
        ):
            raise ValueError("Filter parameters (r, s, e) must be provided together")

        # End date must be >= start date
        if has_start and has_end and end_date < start_date:
            raise ValueError("End date must be greater than or equal to start date")

        # Get all cars if no filter
        if not has_regional:
            return self.cars.find_all()

        # Get cars by regional (in a real system, we'd also filter by availability in date range)
        return self.cars.find_by_regional_id(regional_id)
