from dataclasses import dataclass


@dataclass
class CreateUserDTO:
    """Data Transfer Object for creating a user"""

    username: str
    password: str
    confirm_password: str


@dataclass
class LoginUserDTO:
    """Data Transfer Object for user login"""

    username: str
    password: str


@dataclass
class UpdateUserDTO:
    """Data Transfer Object for updating a user"""

    pass
