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
import jwt
import hashlib
import logging

logger = logging.getLogger(__name__)


def hello(request):
    return HttpResponse("Hello, world.  Badges!!!")


def should_skip_jwt_auth():
    return getattr(settings, 'BADGEKIT_SKIP_JWT_AUTH', False)


def get_jwt_key():
    key = getattr(settings, 'BADGEKIT_JWT_KEY', None)
    if not key:
        logger.error('Got a webhook request, but no BADGEKIT_JWT_KEY configured! Rejecting.')
        raise jwt.DecodeError('No JWT Key')
    return key


@require_POST
@csrf_exempt
def badge_issued_hook(request):
    if not should_skip_jwt_auth():
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            return HttpResponse('JWT auth required', status=401)

        try:
            payload = jwt.decode(auth_header, key=get_jwt_key())
            body_sig = payload['body']['hash']
            # Assuming sha256 for now.
            if body_sig != hashlib.sha256(request.body).hexdigest():
                # Timing attack shouldn't matter: attacker can see the sig anyway.
                return HttpResponse('Bad body signature', status=403)
            # TODO: test method, etc.

        except (jwt.DecodeError, KeyError):
            return HttpResponse('Bad JWT auth', status=403)

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

        models.badge_instance_issued.send_robust(obj, **data)
    except (ValueError, TypeError, ValidationError) as e:
        return HttpResponseBadRequest("Bad JSON request: %s" % str(e))

    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")


class InstanceListView(ListView):
    model = models.BadgeInstanceNotification
