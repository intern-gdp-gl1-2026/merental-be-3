import jwt
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from django.conf import settings

from src.application.schemas.result_enums import LoginErrorCode
from src.application.schemas.user_dto import LoginUserDTO
from src.application.utils.password_utils import verify_password
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


@dataclass
class LoginUserResult:
    """Result of the login user use case"""

    success: bool
    message: str
    token: Optional[str] = None
    error_code: Optional[LoginErrorCode] = None


class LoginUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_dto: LoginUserDTO) -> LoginUserResult:
        """
        Authenticate a user using the provided login data.

        Args:
            user_dto: Data transfer object containing the username and password.

        Returns:
            LoginUserResult: Result indicating whether authentication succeeded,
            including an optional JWT token when successful.
        """
        # Validate input is not None or empty
        if not user_dto.username or not user_dto.password:
            return LoginUserResult(
                success=False,
                message="Invalid credentials",
                error_code=LoginErrorCode.INVALID_INPUT,
            )

        # Normalize username to lowercase for case-insensitive login
        normalized_username = user_dto.username.strip().lower()

        # Check if username exists
        existing_user = self.user_repository.find_by_username(normalized_username)
        if existing_user is None:
            return LoginUserResult(
                success=False,
                message="Invalid credentials",
                error_code=LoginErrorCode.INVALID_CREDENTIALS,
            )

        # Check if password is correct using constant-time comparison
        if not verify_password(user_dto.password, existing_user.password):
            return LoginUserResult(
                success=False,
                message="Invalid credentials",
                error_code=LoginErrorCode.INVALID_CREDENTIALS,
            )

        # Generate JWT token
        token = self._generate_token(existing_user)

        return LoginUserResult(
            success=True, message="User logged in successfully", token=token
        )

    def _generate_token(self, user: User) -> str:
        """Generate a JWT token for the user"""
        now = datetime.now(timezone.utc)

        # Get JWT configuration from settings
        expiration_hours = getattr(settings, "JWT_EXPIRATION_HOURS", 24)
        algorithm = getattr(settings, "JWT_ALGORITHM", "HS256")

        payload = {
            "user_id": user.id,
            "username": user.username,
            "exp": now + timedelta(hours=expiration_hours),
            "iat": now,  # Issued at
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=algorithm)
        return token
