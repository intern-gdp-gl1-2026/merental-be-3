from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.models.user_model import UserModel

class DjangoUserRepository(UserRepository):
    def save(self, user: UserModel)->None:
        # implementation
        pass