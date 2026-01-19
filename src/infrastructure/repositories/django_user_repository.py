from typing import Optional

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.models.user_model import UserModel


class DjangoUserRepository(UserRepository):
    def save(self, user: User) -> User:
        """Save a user entity to the database"""
        user_model = UserModel(username=user.username, password=user.password)
        user_model.save()
        user.id = user_model.id
        return user

    def find_by_username(self, username: str) -> Optional[User]:
        """Find a user by username"""
        try:
            user_model = UserModel.objects.get(username=username)
            return User(
                id=user_model.id,
                username=user_model.username,
                password=user_model.password,
            )
        except UserModel.DoesNotExist:
            return None
