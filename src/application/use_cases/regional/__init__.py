"""Regional use cases package"""

from src.application.use_cases.regional.create_regional import (
    CreateRegionalResult,
    CreateRegionalUseCase,
)
from src.application.use_cases.regional.get_regional import (
    GetRegionalResult,
    GetRegionalUseCase,
)
from src.application.use_cases.regional.get_regionals import (
    GetRegionalsResult,
    GetRegionalsUseCase,
)
from src.application.use_cases.regional.update_regional import (
    UpdateRegionalResult,
    UpdateRegionalUseCase,
)
from src.application.use_cases.regional.delete_regional import (
    DeleteRegionalResult,
    DeleteRegionalUseCase,
)

__all__ = [
    "CreateRegionalResult",
    "CreateRegionalUseCase",
    "GetRegionalResult",
    "GetRegionalUseCase",
    "GetRegionalsResult",
    "GetRegionalsUseCase",
    "UpdateRegionalResult",
    "UpdateRegionalUseCase",
    "DeleteRegionalResult",
    "DeleteRegionalUseCase",
]
