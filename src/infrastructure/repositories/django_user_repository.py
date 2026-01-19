from typing import Optional

from django.db import DatabaseError, IntegrityError

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.models.user_model import UserModel


class DjangoUserRepository(UserRepository):
    def save(self, user: User) -> User:
        """Save a user entity to the database
        
        Args:
            user: User entity to save
            
        Returns:
            User: Saved user entity with ID
            
        Raises:
            IntegrityError: If username already exists (race condition)
            DatabaseError: For other database errors
        """
        try:
            user_model = UserModel(username=user.username, password=user.password)
            user_model.save()
            user.id = user_model.id
            return user
        except IntegrityError:
            # Re-raise IntegrityError for duplicate username handling
            raise
        except DatabaseError:
            # Re-raise DatabaseError for connection issues, etc.
            raise

    def find_by_username(self, username: str) -> Optional[User]:
        """Find a user by username (case-insensitive)
        
        Args:
            username: Username to search for
            
        Returns:
            User entity if found, None otherwise
        """
        try:
            # Use iexact for case-insensitive lookup
            user_model = UserModel.objects.get(username__iexact=username)
            return User(
                id=user_model.id,
                username=user_model.username,
                password=user_model.password,
            )
        except UserModel.DoesNotExist:
            return None
        except DatabaseError:
            # Return None to avoid exposing database issues to the caller
            return None
