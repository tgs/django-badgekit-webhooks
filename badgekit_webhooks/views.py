from __future__ import unicode_literals
from django.conf import settings
import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from . import models
import json


def hello(request):
    return HttpResponse("Hello, world.  Badges!!!")


def should_skip_jwt_auth():
    return getattr(settings, 'BADGEKIT_SKIP_JWT_AUTH', False)


@require_POST
@csrf_exempt
def badge_issued_hook(request):
    if not should_skip_jwt_auth():
        # TODO actually check :)
        return HttpResponse('JWT auth required', status=401)

    try:
        data = json.loads(request.body.decode(request.encoding or 'utf-8'))
        expected_keys = set(['action', 'uid', 'email', 'assertionUrl', 'issuedOn'])
        if type(data) != dict or set(data.keys()) != expected_keys:
            return HttpResponseBadRequest("Unexpected or Missing Fields")

        data['issuedOn'] = datetime.datetime.fromtimestamp(data['issuedOn'])
        del data['action']

        obj = models.BadgeInstanceNotification.objects.create(**data)
        obj.full_clean() # throws ValidationError if fields are bad.
        obj.save()
    except (ValueError, TypeError, ValidationError) as e:
        return HttpResponseBadRequest("Bad JSON request: %s" % str(e))

    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")


class InstanceListView(ListView):
    model = models.BadgeInstanceNotification
