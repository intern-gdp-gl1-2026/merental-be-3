from dataclasses import dataclass


@dataclass
class CreateUserDTO:
    """
    Data Transfer Object for creating a user.

    Note: confirm_password is validated at the API layer before this DTO is created.
    The use case only needs username and password.
    """

    username: str
    password: str


@dataclass
class LoginUserDTO:
    """Data Transfer Object for user login"""

    username: str
    password: str


@dataclass
class UpdateUserDTO:
    """Data Transfer Object for updating a user"""

    pass
