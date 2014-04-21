from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
import json

def hello(request):
    return HttpResponse("Hello, world.  Badges!!!")

@require_POST
def badge_issued_hook(request):
    try:
        data = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest("Bad JSON")

    return HttpResponse("Hello, world.  Badges!!!")
