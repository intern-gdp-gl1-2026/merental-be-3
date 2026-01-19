import hashlib
import jwt
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from django.conf import settings

from src.application.schemas.user_dto import LoginUserDTO
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


@dataclass
class LoginUserResult:
    """Result of the login user use case"""

    success: bool
    message: str
    token: Optional[str] = None


class LoginUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_dto: LoginUserDTO) -> LoginUserResult:
        # Check if username exists
        existing_user = self.user_repository.find_by_username(user_dto.username)
        if existing_user is None:
            return LoginUserResult(success=False, message="Invalid credentials")

        # Check if password is correct
        if self._hash_password(user_dto.password) != existing_user.password:
            return LoginUserResult(success=False, message="Invalid credentials")

        # Generate JWT token
        token = self._generate_token(existing_user)

        return LoginUserResult(
            success=True, message="User logged in successfully", token=token
        )

    def _generate_token(self, user: User) -> str:
        """Generate a JWT token for the user"""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "exp": datetime.now(timezone.utc)
            + timedelta(hours=24),  # Token expires in 24 hours
            "iat": datetime.now(timezone.utc),  # Issued at
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (for simplicity, use bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()
