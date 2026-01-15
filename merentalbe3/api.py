from ninja import NinjaAPI

api = NinjaAPI()


@api.get("/ping", response={200: str})
def ping(request):
    """Simple ping endpoint returning plain text."""
    return "pong"