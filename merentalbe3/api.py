from django.http import HttpResponse
from ninja import NinjaAPI

api = NinjaAPI()


@api.get("/ping")
def ping(request):
    """Simple ping endpoint returning plain text."""
    return HttpResponse("pong", content_type="text/plain")
