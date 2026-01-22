"""Car API endpoints."""

from ninja import Router

from src.api.schemas.car_dto import (
    CreateCarRequest,
    CreateCarResponse,
    UpdateCarRequest,
    UpdateCarResponse,
    GetCarsResponse,
    CarResponse,
    DeleteCarResponse,
    MessageResponse,
)
from src.application.use_cases.car.create_car import CreateCarUseCase
from src.application.use_cases.car.get_cars import GetCarByIdUseCase, GetCarsUseCase
from src.application.use_cases.car.update_car import UpdateCarUseCase
from src.application.use_cases.car.delete_car import DeleteCarUseCase
from src.domain.exceptions import DomainValidationError
from src.infrastructure.repositories.django_car_repository import DjangoCarRepository
from src.infrastructure.repositories.django_regional_repository import (
    DjangoRegionalRepository,
)


router = Router(tags=["Cars"])

# Initialize repositories
cars = DjangoCarRepository()
regionals = DjangoRegionalRepository()


def _car_to_response(car):
    """Convert Car entity to CarResponse DTO."""
    return CarResponse(
        id=car.id,
        name=car.name,
        brand=car.brand,
        model=car.model,
        year=car.year,
        plate_number=car.plate_number,
        color=car.color,
        price_per_day=car.price_per_day,
        regional={
            "id": car.regional_id,
            "name": regionals.find_by_id(car.regional_id).name,
        },
    )


@router.post(
    "", response={201: CreateCarResponse, 400: MessageResponse, 409: MessageResponse}
)
def create_car(request, data: CreateCarRequest):
    """Create a new car.

    Returns:
        201: Car created successfully
        400: Validation error
        409: Plate number already exists
    """
    try:
        use_case = CreateCarUseCase(cars, regionals)
        car = use_case.execute(
            name=data.name,
            brand=data.brand,
            model=data.model,
            year=data.year,
            plate_number=data.plate_number,
            color=data.color,
            price_per_day=data.price_per_day,
            regional_id=data.regional,
        )
        return 201, {
            "message": "Car created successfully",
            "car": _car_to_response(car),
        }
    except DomainValidationError as e:
        return 400, {"message": e.message}
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            return 409, {"message": error_msg}
        return 400, {"message": error_msg}


@router.get("", response={200: GetCarsResponse, 400: MessageResponse})
def get_cars(request, r: int = None, s: int = None, e: int = None):
    """Get all cars with optional filtering.

    Query parameters:
        r: Regional ID
        s: Start date (Unix timestamp)
        e: End date (Unix timestamp)

    All three parameters must be provided together if any is provided.

    Returns:
        200: List of cars
        400: Invalid filter parameters
    """
    try:
        use_case = GetCarsUseCase(cars)
        cars = use_case.execute(regional_id=r, start_date=s, end_date=e)
        return 200, {"cars": [_car_to_response(car) for car in cars]}
    except ValueError as e:
        return 400, {"message": str(e)}


@router.get("{car_id}", response={200: CarResponse, 404: MessageResponse})
def get_car_by_id(request, car_id: int):
    """Get a car by ID.

    Returns:
        200: Car details
        404: Car not found
    """
    try:
        use_case = GetCarByIdUseCase(cars)
        car = use_case.execute(car_id)
        return 200, _car_to_response(car)
    except ValueError as e:
        return 404, {"message": str(e)}


@router.put(
    "{car_id}",
    response={
        200: UpdateCarResponse,
        400: MessageResponse,
        404: MessageResponse,
        409: MessageResponse,
    },
)
def update_car(request, car_id: int, data: UpdateCarRequest):
    """Update a car.

    Supports partial updates - only include fields to update.

    Returns:
        200: Car updated successfully
        400: Validation error
        404: Car not found
        409: Plate number already exists
    """
    try:
        # Build update dict with only provided fields
        update_fields = {}
        if data.name is not None:
            update_fields["name"] = data.name
        if data.brand is not None:
            update_fields["brand"] = data.brand
        if data.model is not None:
            update_fields["model"] = data.model
        if data.year is not None:
            update_fields["year"] = data.year
        if data.plate_number is not None:
            update_fields["plate_number"] = data.plate_number
        if data.color is not None:
            update_fields["color"] = data.color
        if data.price_per_day is not None:
            update_fields["price_per_day"] = data.price_per_day
        if data.regional is not None:
            update_fields["regional_id"] = data.regional

        use_case = UpdateCarUseCase(cars, regionals)
        car = use_case.execute(car_id, **update_fields)
        return 200, {
            "message": "Car updated successfully",
            "car": _car_to_response(car),
        }
    except DomainValidationError as e:
        return 400, {"message": e.message}
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            return 404, {"message": error_msg}
        if "already exists" in error_msg:
            return 409, {"message": error_msg}
        return 400, {"message": error_msg}


@router.delete("{car_id}", response={200: DeleteCarResponse, 404: MessageResponse})
def delete_car(request, car_id: int):
    """Delete a car.

    Returns:
        200: Car deleted successfully
        404: Car not found
    """
    try:
        use_case = DeleteCarUseCase(cars)
        use_case.execute(car_id)
        return 200, {"message": "Car deleted successfully"}
    except ValueError as e:
        return 404, {"message": str(e)}
