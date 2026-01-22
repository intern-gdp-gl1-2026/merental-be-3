from dataclasses import dataclass
from typing import List

from src.domain.entities.regional import Regional
from src.domain.repositories.regional_repository import RegionalRepository


@dataclass
class GetRegionalsResult:
    """Result of the get all regionals use case"""

    success: bool
    message: str
    regionals: List[Regional]


class GetRegionalsUseCase:
    def __init__(self, regionals: RegionalRepository):
        self.regionals = regionals

    def execute(self) -> GetRegionalsResult:
        """
        Get all regionals.

        Returns:
            GetRegionalsResult: Result containing list of all regionals
        """
        regionals = self.regionals.find_all()

        return GetRegionalsResult(
            success=True,
            message="Regionals retrieved successfully",
            regionals=regionals,
        )
