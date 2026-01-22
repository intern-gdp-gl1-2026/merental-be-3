from dataclasses import dataclass
from typing import Optional

from src.application.schemas.result_enums import RegionalErrorCode
from src.domain.entities.regional import Regional
from src.domain.repositories.regional_repository import RegionalRepository


@dataclass
class GetRegionalResult:
    """Result of the get regional by ID use case"""

    success: bool
    message: str
    regional: Optional[Regional] = None
    error_code: Optional[RegionalErrorCode] = None


class GetRegionalUseCase:
    def __init__(self, regionals: RegionalRepository):
        self.regionals = regionals

    def execute(self, regional_id: int) -> GetRegionalResult:
        """
        Get a regional by its ID.

        Args:
            regional_id: The ID of the regional to retrieve

        Returns:
            GetRegionalResult: Result containing the regional if found
        """
        # Validate input
        if not regional_id or regional_id < 1:
            return GetRegionalResult(
                success=False,
                message="Invalid regional ID",
                error_code=RegionalErrorCode.INVALID_INPUT,
            )

        # Find regional by ID
        regional = self.regionals.find_by_id(regional_id)

        if regional is None:
            return GetRegionalResult(
                success=False,
                message="Regional not found",
                error_code=RegionalErrorCode.NOT_FOUND,
            )

        return GetRegionalResult(
            success=True,
            message="Regional retrieved successfully",
            regional=regional,
        )
