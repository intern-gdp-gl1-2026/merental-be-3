"""Regional domain entity with built-in validation."""

from dataclasses import dataclass
from typing import Optional

from src.domain.exceptions import InvalidRegionalNameError


@dataclass
class Regional:
    """
    Regional domain entity.

    Automatically validates and normalizes the regional name on creation.
    The name is trimmed and validated for length requirements.

    Raises:
        InvalidRegionalNameError: If regional name format is invalid
    """

    name: str
    id: Optional[int] = None

    def __post_init__(self):
        """Validate and normalize regional data after initialization."""
        # Normalize name (trim whitespace)
        if self.name:
            self.name = self.name.strip()

        # Validate name
        self._validate_name()

    def _validate_name(self) -> None:
        """
        Validate regional name: required, 2-50 characters.

        Raises:
            InvalidRegionalNameError: If name is empty or has invalid length
        """
        if not self.name:
            raise InvalidRegionalNameError("Regional name is required.")

        if len(self.name) < 2:
            raise InvalidRegionalNameError(
                "Regional name must be at least 2 characters."
            )

        if len(self.name) > 50:
            raise InvalidRegionalNameError(
                "Regional name must not exceed 50 characters."
            )
