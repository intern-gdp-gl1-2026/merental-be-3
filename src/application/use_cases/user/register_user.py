import re
from dataclasses import dataclass
from typing import Optional

from django.db import DatabaseError, IntegrityError, transaction

from src.application.schemas.result_enums import RegisterErrorCode
from src.application.schemas.user_dto import CreateUserDTO
from src.application.utils.password_utils import hash_password
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


# Password validation pattern - special characters for password strength
PASSWORD_SPECIAL_CHARS_PATTERN = r'[!@#$%^&*(),.?":{}|<>_=+/\\;:\[\]~`-]'


@dataclass
class RegisterUserResult:
    """Result of the register user use case"""

    success: bool
    message: str
    user: Optional[User] = None
    error_code: Optional[RegisterErrorCode] = None


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_dto: CreateUserDTO) -> RegisterUserResult:
        """Register a new user based on the provided data.

        This method validates the input data (password confirmation, username
        format, and password strength), checks for existing users with the same
        username, hashes the password, and persists the new user using the
        configured user repository.

        Args:
            user_dto: Data transfer object containing the username, password,
                and password confirmation for the user to register.

        Returns:
            RegisterUserResult: The result of the registration attempt. On
            success, ``success`` is True, ``message`` describes the outcome,
            and ``user`` contains the persisted User instance. On failure,
            ``success`` is False, ``message`` describes the validation or
            business rule violation, and ``user`` is None.
        """
        # Validate input types and non-empty values
        if not self._validate_input_types(user_dto):
            return RegisterUserResult(
                success=False,
                message="Username and password are required",
                error_code=RegisterErrorCode.INVALID_INPUT,
            )

        # Normalize username to lowercase for case-insensitive handling
        normalized_username = user_dto.username.strip().lower()

        # Validate passwords match
        if user_dto.password != user_dto.confirm_password:
            return RegisterUserResult(
                success=False,
                message="Passwords do not match",
                error_code=RegisterErrorCode.PASSWORD_MISMATCH,
            )

        # Validate username format
        if not self._is_valid_username(normalized_username):
            return RegisterUserResult(
                success=False,
                message="Username must be 3-32 characters and contain only letters, numbers, and underscores.",
                error_code=RegisterErrorCode.INVALID_USERNAME,
            )

        # Validate password strength
        if not self._is_valid_password(user_dto.password):
            return RegisterUserResult(
                success=False,
                message=(
                    "Password must be 8-128 characters and contain at least one "
                    "uppercase letter, one lowercase letter, one digit, and one "
                    "special character."
                ),
                error_code=RegisterErrorCode.INVALID_PASSWORD,
            )

        # Check if username already exists (case-insensitive)
        existing_user = self.user_repository.find_by_username(normalized_username)
        if existing_user is not None:
            return RegisterUserResult(
                success=False,
                message="Username already exists",
                error_code=RegisterErrorCode.USERNAME_EXISTS,
            )

        # Hash password and create user
        hashed_password = hash_password(user_dto.password)
        user = User(username=normalized_username, password=hashed_password)

        # Save user with transaction to ensure atomicity
        try:
            with transaction.atomic():
                saved_user = self.user_repository.save(user)
        except IntegrityError:
            # Handle race condition where username was created between check and save
            return RegisterUserResult(
                success=False,
                message="Username already exists",
                error_code=RegisterErrorCode.USERNAME_EXISTS,
            )
        except DatabaseError:
            # Handle database connection or constraint errors
            return RegisterUserResult(
                success=False,
                message="Failed to register user",
                error_code=RegisterErrorCode.DATABASE_ERROR,
            )

        return RegisterUserResult(
            success=True, message="User registered successfully", user=saved_user
        )

    def _validate_input_types(self, user_dto: CreateUserDTO) -> bool:
        """Validate that input fields are non-empty strings"""
        fields = [user_dto.username, user_dto.password, user_dto.confirm_password]
        return all(isinstance(field, str) and field for field in fields)

    def _is_valid_username(self, username: str) -> bool:
        """Validate username: 3-32 chars, alphanumeric and underscore only"""
        if len(username) < 3 or len(username) > 32:
            return False
        return bool(re.match(r"^[a-zA-Z0-9_]+$", username))

    def _is_valid_password(self, password: str) -> bool:
        """Validate password: 8-128 chars, must contain uppercase, lowercase, digit, special char"""
        if len(password) < 8 or len(password) > 128:
            return False
        has_upper = re.search(r"[A-Z]", password) is not None
        has_lower = re.search(r"[a-z]", password) is not None
        has_digit = re.search(r"\d", password) is not None
        # Check for special characters using the defined pattern
        has_special = re.search(PASSWORD_SPECIAL_CHARS_PATTERN, password) is not None
        return has_upper and has_lower and has_digit and has_special
