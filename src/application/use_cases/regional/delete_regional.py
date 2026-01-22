from dataclasses import dataclass
from typing import Optional

from django.db import DatabaseError, transaction

from src.application.schemas.result_enums import RegionalErrorCode
from src.domain.repositories.regional_repository import RegionalRepository


@dataclass
class DeleteRegionalResult:
    """Result of the delete regional use case"""

    success: bool
    message: str
    error_code: Optional[RegionalErrorCode] = None


class DeleteRegionalUseCase:
    def __init__(self, regionals: RegionalRepository):
        self.regionals = regionals

    def execute(self, regional_id: int) -> DeleteRegionalResult:
        """
        Delete a regional by its ID.

        Args:
            regional_id: The ID of the regional to delete

        Returns:
            DeleteRegionalResult: Result indicating whether the regional was deleted successfully
        """
        # Validate regional_id
        if not regional_id or regional_id < 1:
            return DeleteRegionalResult(
                success=False,
                message="Invalid regional ID",
                error_code=RegionalErrorCode.INVALID_INPUT,
            )

        # Find existing regional
        existing_regional = self.regionals.find_by_id(regional_id)
        if existing_regional is None:
            return DeleteRegionalResult(
                success=False,
                message="Regional not found",
                error_code=RegionalErrorCode.NOT_FOUND,
            )

        # Delete regional with transaction
        try:
            with transaction.atomic():
                self.regionals.delete(existing_regional)
        except DatabaseError:
            return DeleteRegionalResult(
                success=False,
                message="Failed to delete regional",
                error_code=RegionalErrorCode.DATABASE_ERROR,
            )

        return DeleteRegionalResult(
            success=True,
            message="Regional deleted successfully",
        )
