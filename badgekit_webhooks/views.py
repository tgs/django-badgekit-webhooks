from __future__ import unicode_literals
import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import models
import json


def hello(request):
    return HttpResponse("Hello, world.  Badges!!!")


@require_POST
@csrf_exempt
def badge_issued_hook(request):
    # TODO validate Authorization header

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
        return HttpResponseBadRequest("Bad JSON request: %s" % e.message)

    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")
