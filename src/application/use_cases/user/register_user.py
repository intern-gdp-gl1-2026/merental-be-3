import hashlib
import re
from dataclasses import dataclass
from typing import Optional

from src.application.schemas.user_dto import CreateUserDTO
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


@dataclass
class RegisterUserResult:
    """Result of the register user use case"""

    success: bool
    message: str
    user: Optional[User] = None


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_dto: CreateUserDTO) -> RegisterUserResult:
        # Validate passwords match
        if user_dto.password != user_dto.confirm_password:
            return RegisterUserResult(success=False, message="Passwords do not match")

        # Validate username format
        if not self._is_valid_username(user_dto.username):
            return RegisterUserResult(success=False, message="Invalid username format")

        # Validate password strength
        if not self._is_valid_password(user_dto.password):
            return RegisterUserResult(
                success=False, message="Password does not meet requirements"
            )

        # Check if username already exists
        existing_user = self.user_repository.find_by_username(user_dto.username)
        if existing_user is not None:
            return RegisterUserResult(success=False, message="Username already exists")

        # Hash password and create user
        hashed_password = self._hash_password(user_dto.password)
        user = User(username=user_dto.username, password=hashed_password)

        # Save user
        saved_user = self.user_repository.save(user)

        return RegisterUserResult(
            success=True, message="User registered successfully", user=saved_user
        )

    def _is_valid_username(self, username: str) -> bool:
        """Validate username: 3-32 chars, alphanumeric and underscore only"""
        if len(username) < 3 or len(username) > 32:
            return False
        return bool(re.match(r"^[a-zA-Z0-9_]+$", username))

    def _is_valid_password(self, password: str) -> bool:
        """Validate password: 8-128 chars, must contain uppercase, lowercase, digit, special char"""
        if len(password) < 8 or len(password) > 128:
            return False
        has_upper = bool(re.search(r"[A-Z]", password))
        has_lower = bool(re.search(r"[a-z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        return has_upper and has_lower and has_digit and has_special

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (for simplicity, use bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()
