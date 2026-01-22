"""Car API endpoints."""

from ninja import Router

from src.api.schemas.car_dto import (
    CreateCarRequest,
    CreateCarResponse,
    UpdateCarRequest,
    UpdateCarResponse,
    GetCarsFilterRequest,
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


def _get_repositories():
    """Dependency injection for repositories."""
    return DjangoCarRepository(), DjangoRegionalRepository()


def _car_to_response(car, regionals_by_id):
    """Convert Car entity to CarResponse DTO.

    Args:
        car: Car entity to convert
        regionals_by_id: Dictionary of regionals indexed by ID {id: regional}
    """
    regional = regionals_by_id.get(car.regional_id)
    if not regional:
        raise ValueError(f"Regional with ID {car.regional_id} not found")
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
            "name": regional.name,
        },
    )


@router.post(
    "/", response={201: CreateCarResponse, 400: MessageResponse, 409: MessageResponse}
)
def create_car(request, data: CreateCarRequest):
    """Create a new car.

    Returns:
        201: Car created successfully
        400: Validation error
        409: Plate number already exists
    """
    try:
        cars_repo, regionals_repo = _get_repositories()
        use_case = CreateCarUseCase(cars_repo, regionals_repo)
        created_car = use_case.execute(
            name=data.name,
            brand=data.brand,
            model=data.model,
            year=data.year,
            plate_number=data.plate_number,
            color=data.color,
            price_per_day=data.price_per_day,
            regional_id=data.regional,
        )
        # Build regionals lookup dict for response conversion
        regional = regionals_repo.find_by_id(created_car.regional_id)
        if not regional:
            return 400, {
                "message": f"Regional with ID {created_car.regional_id} not found"
            }
        regionals_by_id = {regional.id: regional}
        return 201, {
            "message": "Car created successfully",
            "car": _car_to_response(created_car, regionals_by_id),
        }
    except DomainValidationError as e:
        return 400, {"message": e.message}
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            return 409, {"message": error_msg}
        return 400, {"message": error_msg}


@router.get("/", response={200: GetCarsResponse, 400: MessageResponse})
def get_cars(request, filters: GetCarsFilterRequest = None):
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
        cars_repo, regionals_repo = _get_repositories()
        use_case = GetCarsUseCase(cars_repo)
        car_list = use_case.execute(
            regional_id=filters.r if filters else None,
            start_date=filters.s if filters else None,
            end_date=filters.e if filters else None,
        )

        # Fetch all regionals upfront to avoid N+1 queries
        all_regionals = regionals_repo.find_all()
        regionals_by_id = {regional.id: regional for regional in all_regionals}

        return 200, {
            "cars": [_car_to_response(car, regionals_by_id) for car in car_list]
        }
    except ValueError as e:
        return 400, {"message": str(e)}


@router.get("/{car_id}", response={200: CarResponse, 404: MessageResponse})
def get_car_by_id(request, car_id: int):
    """Get a car by ID.

    Returns:
        200: Car details
        404: Car not found
    """
    try:
        cars_repo, regionals_repo = _get_repositories()
        use_case = GetCarByIdUseCase(cars_repo)
        retrieved_car = use_case.execute(car_id)

        # Build regionals lookup dict for response conversion
        regional = regionals_repo.find_by_id(retrieved_car.regional_id)
        if not regional:
            return 404, {
                "message": f"Regional with ID {retrieved_car.regional_id} not found"
            }
        regionals_by_id = {regional.id: regional}

        return 200, _car_to_response(retrieved_car, regionals_by_id)
    except ValueError as e:
        return 404, {"message": str(e)}


@router.put(
    "/{car_id}",
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
        update_fields = data.model_dump(exclude_none=True)
        # Rename 'regional' to 'regional_id' for domain entity
        if "regional" in update_fields:
            update_fields["regional_id"] = update_fields.pop("regional")

        cars_repo, regionals_repo = _get_repositories()
        use_case = UpdateCarUseCase(cars_repo, regionals_repo)
        updated_car = use_case.execute(car_id, **update_fields)

        # Build regionals lookup dict for response conversion
        regional = regionals_repo.find_by_id(updated_car.regional_id)
        if not regional:
            return 400, {
                "message": f"Regional with ID {updated_car.regional_id} not found"
            }
        regionals_by_id = {regional.id: regional}

        return 200, {
            "message": "Car updated successfully",
            "car": _car_to_response(updated_car, regionals_by_id),
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


@router.delete("/{car_id}", response={200: DeleteCarResponse, 404: MessageResponse})
def delete_car(request, car_id: int):
    """Delete a car.

    Returns:
        200: Car deleted successfully
        404: Car not found
    """
    try:
        cars_repo, _ = _get_repositories()
        use_case = DeleteCarUseCase(cars_repo)
        use_case.execute(car_id)
        return 200, {"message": "Car deleted successfully"}
    except ValueError as e:
        return 404, {"message": str(e)}
