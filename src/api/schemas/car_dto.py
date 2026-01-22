from ninja import Schema
from pydantic import field_validator


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

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or len(v) < 3 or len(v) > 100:
            raise ValueError("Name must be between 3 and 100 characters")
        return v

    @field_validator("brand")
    @classmethod
    def validate_brand(cls, v: str) -> str:
        if not v or len(v) < 2 or len(v) > 50:
            raise ValueError("Brand must be between 2 and 50 characters")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        if not v or len(v) < 1 or len(v) > 50:
            raise ValueError("Model must be between 1 and 50 characters")
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        if v < 1900 or v > 2027:
            raise ValueError("Year must be between 1900 and 2027")
        return v

    @field_validator("plate_number")
    @classmethod
    def validate_plate_number(cls, v: str) -> str:
        if not v or len(v) < 3 or len(v) > 20:
            raise ValueError("Plate number must be between 3 and 20 characters")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not v or len(v) < 2 or len(v) > 30:
            raise ValueError("Color must be between 2 and 30 characters")
        return v

    @field_validator("price_per_day")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Price per day must be non-negative")
        return v


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

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v is None:
            return v
        if not v or len(v) < 3 or len(v) > 100:
            raise ValueError("Name must be between 3 and 100 characters")
        return v

    @field_validator("brand", mode="before")
    @classmethod
    def validate_brand(cls, v: str) -> str:
        if v is None:
            return v
        if not v or len(v) < 2 or len(v) > 50:
            raise ValueError("Brand must be between 2 and 50 characters")
        return v

    @field_validator("model", mode="before")
    @classmethod
    def validate_model(cls, v: str) -> str:
        if v is None:
            return v
        if not v or len(v) < 1 or len(v) > 50:
            raise ValueError("Model must be between 1 and 50 characters")
        return v

    @field_validator("year", mode="before")
    @classmethod
    def validate_year(cls, v: int) -> int:
        if v is None:
            return v
        if v < 1900 or v > 2027:
            raise ValueError("Year must be between 1900 and 2027")
        return v

    @field_validator("plate_number", mode="before")
    @classmethod
    def validate_plate_number(cls, v: str) -> str:
        if v is None:
            return v
        if not v or len(v) < 3 or len(v) > 20:
            raise ValueError("Plate number must be between 3 and 20 characters")
        return v

    @field_validator("color", mode="before")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if v is None:
            return v
        if not v or len(v) < 2 or len(v) > 30:
            raise ValueError("Color must be between 2 and 30 characters")
        return v

    @field_validator("price_per_day", mode="before")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v is None:
            return v
        if v < 0:
            raise ValueError("Price per day must be non-negative")
        return v


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
