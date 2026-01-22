from ninja import NinjaAPI

from src.api.users import router as auth_router
from src.api.regionals import router as regional_router

api = NinjaAPI()

# Include auth routes
api.add_router("/auth", auth_router)

# Include regional routes
api.add_router("/regionals", regional_router)


@api.get("/ping", response={200: str})
def ping(request):
    """Simple ping endpoint returning plain text."""
    return "pong"
