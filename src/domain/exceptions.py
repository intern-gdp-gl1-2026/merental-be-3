"""Domain exceptions for validation errors."""


class DomainValidationError(ValueError):
    """Base exception for domain validation errors"""

    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.message = message
        self.code = code


class InvalidUsernameError(DomainValidationError):
    """Raised when username format is invalid"""

    def __init__(
        self,
        message: str = "Username must be 3-32 characters and contain only letters, numbers, and underscores.",
    ):
        super().__init__(message, "INVALID_USERNAME")


class InvalidPasswordError(DomainValidationError):
    """Raised when password does not meet strength requirements"""

    def __init__(
        self,
        message: str = (
            "Password must be 8-128 characters and contain at least one "
            "uppercase letter, one lowercase letter, one digit, and one "
            "special character."
        ),
    ):
        super().__init__(message, "INVALID_PASSWORD")
