from ninja import Router, Schema

from src.application.schemas.user_dto import CreateUserDTO
from src.application.use_cases.user.register_user import RegisterUserUseCase
from src.infrastructure.repositories.django_user_repository import DjangoUserRepository


router = Router(tags=["auth"])


class RegisterRequest(Schema):
    """Request schema for user registration"""

    username: str
    password: str
    confirmPassword: str


class MessageResponse(Schema):
    """Response schema with message"""

    message: str


@router.post(
    "/register",
    response={201: MessageResponse, 400: MessageResponse, 409: MessageResponse},
)
def register(request, payload: RegisterRequest):
    """Register a new user"""
    # Create DTO from request
    user_dto = CreateUserDTO(
        username=payload.username,
        password=payload.password,
        confirm_password=payload.confirmPassword,
    )

    # Execute use case
    user_repository = DjangoUserRepository()
    use_case = RegisterUserUseCase(user_repository)
    result = use_case.execute(user_dto)

    # Return response based on result
    if result.success:
        return 201, {"message": result.message}
    elif result.message == "Username already exists":
        return 409, {"message": result.message}
    else:
        return 400, {"message": result.message}
