from ninja import NinjaAPI

from src.api.users import router as auth_router

api = NinjaAPI()

# Include auth routes
api.add_router("/auth", auth_router)


@api.get("/ping", response={200: str})
def ping(request):
    """Simple ping endpoint returning plain text."""
    return "pong"
