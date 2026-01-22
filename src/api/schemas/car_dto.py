from ninja import Schema


class CreateCarRequest(Schema):
    """Request schema for creating a car"""

    name: str
    brand: str
    model: str
    year: int
    plate_number: str
    color: str
    price_per_day: float
    regional: int


class UpdateCarRequest(Schema):
    """Request schema for updating a car (all fields optional)"""

    name: str = None
    brand: str = None
    model: str = None
    year: int = None
    plate_number: str = None
    color: str = None
    price_per_day: float = None
    regional: int = None


class RegionalResponse(Schema):
    """Response schema for Regional"""

    id: int
    name: str


class CarResponse(Schema):
    """Response schema for Car"""

    id: int
    name: str
    brand: str
    model: str
    year: int
    plate_number: str
    color: str
    price_per_day: float
    regional: RegionalResponse


class CreateCarResponse(Schema):
    """Response schema for creating a car"""

    message: str
    car: CarResponse


class GetCarsFilterRequest(Schema):
    """Query parameters for filtering cars"""

    r: int = None  # Regional ID
    s: int = None  # Start date (Unix timestamp)
    e: int = None  # End date (Unix timestamp)


class GetCarsResponse(Schema):
    """Response schema for getting all cars"""

    cars: list[CarResponse]


class UpdateCarResponse(Schema):
    """Response schema for updating a car"""

    message: str
    car: CarResponse


class DeleteCarResponse(Schema):
    """Response schema for deleting a car"""

    message: str


class MessageResponse(Schema):
    """Response schema with just a message"""

    message: str
