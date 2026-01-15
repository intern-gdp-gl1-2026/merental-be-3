from src.domain.repositories.user_repository import UserRepository
from src.domain.entities.user import User

class DjangoUserRepository(UserRepository):
    def save(self, user: User)->None:
        # implementation
        pass