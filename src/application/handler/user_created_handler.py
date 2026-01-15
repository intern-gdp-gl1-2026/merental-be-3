from src.domain.events.user_created import UserCreated

class UserCreatedHandler:
    def __init__(self):
        pass
    
    @staticmethod
    def handle(event: UserCreated):
        pass