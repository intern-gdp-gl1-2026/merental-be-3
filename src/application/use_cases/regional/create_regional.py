from dataclasses import dataclass
from typing import Optional

from django.db import DatabaseError, IntegrityError, transaction

from src.application.schemas.result_enums import RegionalErrorCode
from src.domain.entities.regional import Regional
from src.domain.exceptions import InvalidRegionalNameError
from src.domain.repositories.regional_repository import RegionalRepository


@dataclass
class CreateRegionalResult:
    """Result of the create regional use case"""

    success: bool
    message: str
    regional: Optional[Regional] = None
    error_code: Optional[RegionalErrorCode] = None


class CreateRegionalUseCase:
    def __init__(self, regionals: RegionalRepository):
        self.regionals = regionals

    def execute(self, name: str) -> CreateRegionalResult:
        """
        Create a regional using the provided name.

        Args:
            name: The name of the regional to create

        Returns:
            CreateRegionalResult: Result indicating whether the regional was created successfully,
            including an optional regional when successful.
        """
        # Try to create Regional entity - validation happens automatically in __post_init__
        try:
            regional = Regional(name=name)
        except InvalidRegionalNameError as e:
            return CreateRegionalResult(
                success=False,
                message=e.message,
                error_code=RegionalErrorCode.INVALID_INPUT,
            )

        # Save regional with transaction to ensure atomicity
        try:
            with transaction.atomic():
                saved_regional = self.regionals.save(regional)
        except IntegrityError:
            # Handle duplicate name error
            return CreateRegionalResult(
                success=False,
                message="Regional with this name already exists",
                error_code=RegionalErrorCode.ALREADY_EXISTS,
            )
        except DatabaseError:
            # Handle database connection or constraint errors
            return CreateRegionalResult(
                success=False,
                message="Failed to create regional",
                error_code=RegionalErrorCode.DATABASE_ERROR,
            )

        return CreateRegionalResult(
            success=True,
            message="Regional created successfully",
            regional=saved_regional,
        )
