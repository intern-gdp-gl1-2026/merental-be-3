from abc import ABC, abstractmethod
from src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        pass
