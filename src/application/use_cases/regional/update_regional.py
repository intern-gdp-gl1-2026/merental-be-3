from dataclasses import dataclass
from typing import Optional

from django.db import DatabaseError, transaction

from src.application.schemas.result_enums import RegionalErrorCode
from src.domain.entities.regional import Regional
from src.domain.exceptions import InvalidRegionalNameError
from src.domain.repositories.regional_repository import RegionalRepository


@dataclass
class UpdateRegionalResult:
    """Result of the update regional use case"""

    success: bool
    message: str
    regional: Optional[Regional] = None
    error_code: Optional[RegionalErrorCode] = None


class UpdateRegionalUseCase:
    def __init__(self, regionals: RegionalRepository):
        self.regionals = regionals

    def execute(self, regional_id: int, name: str) -> UpdateRegionalResult:
        """
        Update a regional using the provided ID and new name.

        Args:
            regional_id: The ID of the regional to update
            name: The new name for the regional

        Returns:
            UpdateRegionalResult: Result indicating whether the regional was updated successfully
        """
        # Validate regional_id
        if not regional_id or regional_id < 1:
            return UpdateRegionalResult(
                success=False,
                message="Invalid regional ID",
                error_code=RegionalErrorCode.INVALID_INPUT,
            )

        # Find existing regional
        existing_regional = self.regionals.find_by_id(regional_id)
        if existing_regional is None:
            return UpdateRegionalResult(
                success=False,
                message="Regional not found",
                error_code=RegionalErrorCode.NOT_FOUND,
            )

        # Validate new name by creating a temporary Regional entity
        # Validation happens automatically in __post_init__
        try:
            validated_regional = Regional(name=name, id=existing_regional.id)
        except InvalidRegionalNameError as e:
            return UpdateRegionalResult(
                success=False,
                message=e.message,
                error_code=RegionalErrorCode.INVALID_INPUT,
            )

        # Save updated regional with transaction
        try:
            with transaction.atomic():
                updated_regional = self.regionals.update(validated_regional)
        except DatabaseError:
            return UpdateRegionalResult(
                success=False,
                message="Failed to update regional",
                error_code=RegionalErrorCode.DATABASE_ERROR,
            )

        return UpdateRegionalResult(
            success=True,
            message="Regional updated successfully",
            regional=updated_regional,
        )
