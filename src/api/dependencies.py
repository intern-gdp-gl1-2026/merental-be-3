"""Dependency injection container for the application"""

from functools import lru_cache

from src.application.use_cases.user.login_user import LoginUserUseCase
from src.application.use_cases.user.register_user import RegisterUserUseCase
from src.application.use_cases.regional.create_regional import CreateRegionalUseCase
from src.application.use_cases.regional.get_regional import GetRegionalUseCase
from src.application.use_cases.regional.get_regionals import GetRegionalsUseCase
from src.application.use_cases.regional.update_regional import UpdateRegionalUseCase
from src.application.use_cases.regional.delete_regional import DeleteRegionalUseCase
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.regional_repository import RegionalRepository
from src.infrastructure.repositories.django_user_repository import DjangoUserRepository
from src.infrastructure.repositories.django_regional_repository import (
    DjangoRegionalRepository,
)


@lru_cache()
def get_user_repository() -> UserRepository:
    """Get the user repository instance (singleton)"""
    return DjangoUserRepository()


@lru_cache()
def get_regional_repository() -> RegionalRepository:
    """Get the regional repository instance (singleton)"""
    return DjangoRegionalRepository()


def get_register_use_case() -> RegisterUserUseCase:
    """Get the register user use case with dependencies injected"""
    return RegisterUserUseCase(get_user_repository())


def get_login_use_case() -> LoginUserUseCase:
    """Get the login user use case with dependencies injected"""
    return LoginUserUseCase(get_user_repository())


def get_create_regional_use_case() -> CreateRegionalUseCase:
    """Get the create regional use case with dependencies injected"""
    return CreateRegionalUseCase(get_regional_repository())


def get_get_regional_use_case() -> GetRegionalUseCase:
    """Get the get regional use case with dependencies injected"""
    return GetRegionalUseCase(get_regional_repository())


def get_get_regionals_use_case() -> GetRegionalsUseCase:
    """Get the get all regionals use case with dependencies injected"""
    return GetRegionalsUseCase(get_regional_repository())


def get_update_regional_use_case() -> UpdateRegionalUseCase:
    """Get the update regional use case with dependencies injected"""
    return UpdateRegionalUseCase(get_regional_repository())


def get_delete_regional_use_case() -> DeleteRegionalUseCase:
    """Get the delete regional use case with dependencies injected"""
    return DeleteRegionalUseCase(get_regional_repository())
