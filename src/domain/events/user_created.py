@dataclass(frozen=True)
class UserCreated:
    """Event emitted when a new user is created"""
    email: str
    pass