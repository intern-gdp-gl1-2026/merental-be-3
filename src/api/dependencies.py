"""Dependency injection container for the application"""
from functools import lru_cache

from src.application.use_cases.user.login_user import LoginUserUseCase
from src.application.use_cases.user.register_user import RegisterUserUseCase
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.repositories.django_user_repository import DjangoUserRepository


@lru_cache()
def get_user_repository() -> UserRepository:
    """Get the user repository instance (singleton)"""
    return DjangoUserRepository()


def get_register_use_case() -> RegisterUserUseCase:
    """Get the register user use case with dependencies injected"""
    return RegisterUserUseCase(get_user_repository())


def get_login_use_case() -> LoginUserUseCase:
    """Get the login user use case with dependencies injected"""
    return LoginUserUseCase(get_user_repository())
