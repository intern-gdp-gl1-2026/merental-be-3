"""User domain entity with built-in validation."""

import re
from dataclasses import dataclass, field
from typing import Optional

from src.domain.exceptions import InvalidPasswordError, InvalidUsernameError

# Password validation pattern - special characters for password strength
PASSWORD_SPECIAL_CHARS_PATTERN = r'[!@#$%^&*(),.?":{}|<>_=+/\\;:\[\]~`-]'


@dataclass
class User:
    """
    User domain entity.

    Automatically validates username and password on creation.
    Validation only happens when is_hashed=False (for new users with plain passwords).
    When loading from database with hashed password, set is_hashed=True to skip validation.

    Raises:
        InvalidUsernameError: If username format is invalid
        InvalidPasswordError: If password doesn't meet strength requirements (only when is_hashed=False)
    """

    username: str
    password: str
    id: Optional[int] = None
    is_hashed: bool = field(default=False, repr=False)

    def __post_init__(self):
        """Validate user data after initialization."""
        # Normalize username
        self.username = self.username.strip().lower()

        # Always validate username format
        self._validate_username()

        # Only validate password strength for new users (unhashed passwords)
        if not self.is_hashed:
            self._validate_password()

    def _validate_username(self) -> None:
        """
        Validate username format: 3-32 chars, alphanumeric and underscore only.

        Raises:
            InvalidUsernameError: If username format is invalid
        """
        if len(self.username) < 3 or len(self.username) > 32:
            raise InvalidUsernameError()
        if not re.match(r"^[a-zA-Z0-9_]+$", self.username):
            raise InvalidUsernameError()

    def _validate_password(self) -> None:
        """
        Validate password strength: 8-128 chars, must contain uppercase,
        lowercase, digit, and special character.

        Raises:
            InvalidPasswordError: If password doesn't meet strength requirements
        """
        if len(self.password) < 8 or len(self.password) > 128:
            raise InvalidPasswordError()
        has_upper = re.search(r"[A-Z]", self.password) is not None
        has_lower = re.search(r"[a-z]", self.password) is not None
        has_digit = re.search(r"\d", self.password) is not None
        has_special = (
            re.search(PASSWORD_SPECIAL_CHARS_PATTERN, self.password) is not None
        )
        if not (has_upper and has_lower and has_digit and has_special):
            raise InvalidPasswordError()
