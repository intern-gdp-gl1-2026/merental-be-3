from django_ratelimit.decorators import ratelimit
from ninja import Router

from src.api.dependencies import get_login_use_case, get_register_use_case
from src.application.schemas.result_enums import RegisterErrorCode
from src.api.schemas.user_dto import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
)


router = Router(tags=["auth"])


@router.post(
    "/register",
    response={201: MessageResponse, 400: MessageResponse, 409: MessageResponse},
)
@ratelimit(key="ip", rate="5/m", method="POST")
def register(request, payload: RegisterRequest):
    """Register a new user

    Rate limited to 5 requests per minute per IP address.
    Note: Ensure X-Forwarded-For headers are properly configured if behind a proxy.
    """
    # Execute use case directly with the schema
    use_case = get_register_use_case()
    result = use_case.execute(payload.username, payload.password)

    # Return response based on error code
    if result.success:
        return 201, {"message": result.message}
    elif result.error_code == RegisterErrorCode.USERNAME_EXISTS:
        return 409, {"message": result.message}
    else:
        return 400, {"message": result.message}


@router.post(
    "/login",
    response={200: LoginResponse, 401: MessageResponse},
)
@ratelimit(key="ip", rate="10/m", method="POST")
def login(request, payload: LoginRequest):
    """Login a user

    Rate limited to 10 requests per minute per IP address to prevent brute-force attacks.
    Note: Ensure X-Forwarded-For headers are properly configured if behind a proxy.
    """
    # Execute use case directly with the schema
    use_case = get_login_use_case()
    result = use_case.execute(payload.username, payload.password)

    # Return response based on result
    if result.success:
        return 200, {"message": result.message, "token": result.token}
    else:
        return 401, {"message": result.message}
