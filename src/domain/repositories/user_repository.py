from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        """Save a user to the repository and return the saved user"""
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """Find a user by username, returns None if not found"""
        pass
