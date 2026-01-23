"""Car domain entity with built-in validation."""

from dataclasses import dataclass
from typing import Optional

from src.domain.exceptions import DomainValidationError


# Validation constants
CAR_NAME_MIN, CAR_NAME_MAX = 3, 100
BRAND_MIN, BRAND_MAX = 2, 50
MODEL_MIN, MODEL_MAX = 1, 50
YEAR_MIN, YEAR_MAX = 1900, 2027
PLATE_NUMBER_MIN, PLATE_NUMBER_MAX = 3, 20
COLOR_MIN, COLOR_MAX = 2, 30


@dataclass
class Car:
    """
    Car domain entity.

    Represents a car in the rental system with all necessary information
    for renting and management.

    Attributes:
        name: Full name/description of the car (e.g., "Toyota Camry 2023")
        brand: Car brand (e.g., "Toyota")
        model: Car model (e.g., "Camry")
        year: Manufacturing year
        plate_number: License plate number (unique)
        color: Car color
        price_per_day: Daily rental price
        regional_id: Regional/location ID where car is available
        id: Unique identifier (set by repository on save)
    """

    name: str
    brand: str
    model: str
    year: int
    plate_number: str
    color: str
    price_per_day: float
    regional_id: int
    id: Optional[int] = None

    def __post_init__(self):
        """Validate car data after initialization."""
        self._validate_all()

    def _validate_all(self) -> None:
        """Validate all car fields."""
        self._validate_name()
        self._validate_brand()
        self._validate_model()
        self._validate_year()
        self._validate_plate_number()
        self._validate_color()
        self._validate_price_per_day()
        self._validate_regional_id()

    def _validate_name(self) -> None:
        """Validate name format.

        Raises:
            DomainValidationError: If name is invalid
        """
        if (
            not self.name
            or len(self.name) < CAR_NAME_MIN
            or len(self.name) > CAR_NAME_MAX
        ):
            raise DomainValidationError(
                f"Name must be between {CAR_NAME_MIN} and {CAR_NAME_MAX} characters",
                "INVALID_CAR_NAME",
            )

    def _validate_brand(self) -> None:
        """Validate brand format.

        Raises:
            DomainValidationError: If brand is invalid
        """
        if not self.brand or len(self.brand) < BRAND_MIN or len(self.brand) > BRAND_MAX:
            raise DomainValidationError(
                f"Brand must be between {BRAND_MIN} and {BRAND_MAX} characters",
                "INVALID_BRAND",
            )

    def _validate_model(self) -> None:
        """Validate model format.

        Raises:
            DomainValidationError: If model is invalid
        """
        if not self.model or len(self.model) < MODEL_MIN or len(self.model) > MODEL_MAX:
            raise DomainValidationError(
                f"Model must be between {MODEL_MIN} and {MODEL_MAX} characters",
                "INVALID_MODEL",
            )

    def _validate_year(self) -> None:
        """Validate year format.

        Raises:
            DomainValidationError: If year is invalid
        """
        if (
            not isinstance(self.year, int)
            or self.year < YEAR_MIN
            or self.year > YEAR_MAX
        ):
            raise DomainValidationError(
                f"Year must be between {YEAR_MIN} and {YEAR_MAX}", "INVALID_YEAR"
            )

    def _validate_plate_number(self) -> None:
        """Validate plate number format.

        Raises:
            DomainValidationError: If plate number is invalid
        """
        if (
            not self.plate_number
            or len(self.plate_number) < PLATE_NUMBER_MIN
            or len(self.plate_number) > PLATE_NUMBER_MAX
        ):
            raise DomainValidationError(
                f"Plate number must be between {PLATE_NUMBER_MIN} and {PLATE_NUMBER_MAX} characters",
                "INVALID_PLATE_NUMBER",
            )

    def _validate_color(self) -> None:
        """Validate color format.

        Raises:
            DomainValidationError: If color is invalid
        """
        if not self.color or len(self.color) < COLOR_MIN or len(self.color) > COLOR_MAX:
            raise DomainValidationError(
                f"Color must be between {COLOR_MIN} and {COLOR_MAX} characters",
                "INVALID_COLOR",
            )

    def _validate_price_per_day(self) -> None:
        """Validate price per day.

        Raises:
            DomainValidationError: If price is invalid
        """
        if not isinstance(self.price_per_day, (int, float)) or self.price_per_day < 0:
            raise DomainValidationError(
                "Price per day must be a non-negative number", "INVALID_PRICE"
            )

    def _validate_regional_id(self) -> None:
        """Validate regional ID.

        Raises:
            DomainValidationError: If regional_id is invalid
        """
        if not isinstance(self.regional_id, int) or self.regional_id <= 0:
            raise DomainValidationError(
                "Regional ID must be a positive integer", "INVALID_REGIONAL_ID"
            )

    def update(self, **kwargs) -> None:
        """Update car fields with validation.

        Allows partial updates - only provided fields are updated.

        Args:
            **kwargs: Fields to update (e.g., color="Black")

        Raises:
            DomainValidationError: If any updated field is invalid
        """
        allowed_fields = {
            "name",
            "brand",
            "model",
            "year",
            "plate_number",
            "color",
            "price_per_day",
            "regional_id",
        }
        for key, value in kwargs.items():
            if key not in allowed_fields:
                raise DomainValidationError(
                    f"Cannot update field '{key}'", "INVALID_FIELD"
                )
            setattr(self, key, value)

        # Re-validate all fields after update
        self._validate_all()
