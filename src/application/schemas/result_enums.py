"""Enums for use case results"""

from enum import Enum


class RegisterErrorCode(Enum):
    """Error codes for user registration"""

    PASSWORD_MISMATCH = "passwords_do_not_match"
    INVALID_USERNAME = "invalid_username"
    INVALID_PASSWORD = "invalid_password"
    INVALID_INPUT = "invalid_input"
    USERNAME_EXISTS = "username_exists"
    DATABASE_ERROR = "database_error"


class LoginErrorCode(Enum):
    """Error codes for user login"""

    INVALID_CREDENTIALS = "invalid_credentials"
    INVALID_INPUT = "invalid_input"


class RegionalErrorCode(Enum):
    """Error codes for regional operations"""

    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    DATABASE_ERROR = "database_error"
