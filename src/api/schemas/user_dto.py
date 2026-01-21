from ninja import Schema
from pydantic import model_validator


class RegisterRequest(Schema):
    """Request schema for user registration with password confirmation validation"""

    username: str
    password: str
    confirmPassword: str

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "RegisterRequest":
        """Validate that password and confirmPassword match"""
        if self.password != self.confirmPassword:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(Schema):
    """Request schema for user login"""

    username: str
    password: str


class MessageResponse(Schema):
    """Response schema with message"""

    message: str


class LoginResponse(Schema):
    """Response schema for user login"""

    message: str
    token: str
