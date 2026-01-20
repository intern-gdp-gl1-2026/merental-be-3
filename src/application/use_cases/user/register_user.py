from dataclasses import dataclass
from typing import Optional

from django.db import DatabaseError, IntegrityError, transaction

from src.application.schemas.result_enums import RegisterErrorCode
from src.application.utils.password_utils import hash_password
from src.domain.entities.user import User
from src.domain.exceptions import InvalidPasswordError, InvalidUsernameError
from src.domain.repositories.user_repository import UserRepository


@dataclass
class RegisterUserResult:
    """Result of the register user use case"""

    success: bool
    message: str
    user: Optional[User] = None
    error_code: Optional[RegisterErrorCode] = None


class RegisterUserUseCase:
    def __init__(self, users: UserRepository):
        self.users = users

    def execute(self, username: str, password: str) -> RegisterUserResult:
        """Register a new user based on the provided data.

        This method validates the input data through the User entity,
        checks for existing users with the same username, hashes the password,
        and persists the new user using the configured user repository.

        Note: Password confirmation should be validated at the API layer
        before calling this use case.

        Args:
            username: The username for the new user
            password: The password for the new user (will be hashed before saving)

        Returns:
            RegisterUserResult: The result of the registration attempt. On
            success, ``success`` is True, ``message`` describes the outcome,
            and ``user`` contains the persisted User instance. On failure,
            ``success`` is False, ``message`` describes the validation or
            business rule violation, and ``user`` is None.
        """
        # Validate input types and non-empty values
        if not username or not password:
            return RegisterUserResult(
                success=False,
                message="Username and password are required",
                error_code=RegisterErrorCode.INVALID_INPUT,
            )

        # Try to create User entity - validation happens automatically
        try:
            user = User(username=username, password=password)
        except InvalidUsernameError as e:
            return RegisterUserResult(
                success=False,
                message=e.message,
                error_code=RegisterErrorCode.INVALID_USERNAME,
            )
        except InvalidPasswordError as e:
            return RegisterUserResult(
                success=False,
                message=e.message,
                error_code=RegisterErrorCode.INVALID_PASSWORD,
            )

        # Check if username already exists (case-insensitive - username is already normalized)
        existing_user = self.users.find_by_username(user.username)
        if existing_user is not None:
            return RegisterUserResult(
                success=False,
                message="Username already exists",
                error_code=RegisterErrorCode.USERNAME_EXISTS,
            )

        # Hash password before saving
        hashed_password = hash_password(user.password)
        user_to_save = User(
            username=user.username, password=hashed_password, is_hashed=True
        )

        # Save user with transaction to ensure atomicity
        try:
            with transaction.atomic():
                saved_user = self.users.save(user_to_save)
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
