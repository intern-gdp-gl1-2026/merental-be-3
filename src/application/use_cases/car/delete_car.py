"""Use case for deleting a car."""

from src.domain.repositories.car_repository import CarRepository


class DeleteCarUseCase:
    """Delete an existing car."""

    def __init__(self, cars: CarRepository):
        self.cars = cars

    def execute(self, car_id: int) -> None:
        """Delete a car.

        Args:
            car_id: The car ID to delete

        Raises:
            ValueError: If car not found
        """
        car = self.cars.find_by_id(car_id)
        if not car:
            raise ValueError(f"Car with ID {car_id} not found")

        self.cars.delete(car)
