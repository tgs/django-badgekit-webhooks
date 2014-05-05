from __future__ import unicode_literals
import re
from django.conf import settings
import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.template.loader import render_to_string
from django.utils.encoding import smart_bytes
from . import models
import json
import jwt
import hashlib
import logging
from django.core.urlresolvers import reverse
from . import utils


logger = logging.getLogger(__name__)


def hello(request):
    return HttpResponse("Hello, world.  Badges!!!")


def get_jwt_key():
    key = settings.BADGEKIT_JWT_KEY
    if not key:
        logger.error('Got a webhook request, but no BADGEKIT_JWT_KEY configured! Rejecting.')
        raise jwt.DecodeError('No JWT Key')
    return key


auth_header_re = re.compile(r'JWT token="([0-9A-Za-z-_.]+)"')


@require_POST
@csrf_exempt
def badge_issued_hook(request):
    if not settings.BADGEKIT_SKIP_JWT_AUTH:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            return HttpResponse('JWT auth required', status=401)
        match = auth_header_re.match(auth_header)
        if not match:
            logger.info("Bad auth header: <<%s>>" % repr(auth_header))
            return HttpResponse('Malformed Authorization header', status=403)

        auth_token = match.group(1)

        try:
            payload = jwt.decode(auth_token, key=get_jwt_key())
            body_sig = payload['body']['hash']
            # Assuming sha256 for now.
            if body_sig != hashlib.sha256(request.body).hexdigest():
                logger.warning("Bad JWT signature on webhook body")
                return HttpResponse('Bad body signature', status=403)

        except (jwt.DecodeError, KeyError):
            logger.exception('Bad JWT auth')
            return HttpResponse('Bad JWT auth', status=403)

    try:
        data = json.loads(request.body.decode(request.encoding or 'utf-8'))
        expected_keys = set(['action', 'uid', 'email', 'assertionUrl', 'issuedOn'])
        if type(data) != dict:
            return HttpResponseBadRequest("Not a JSON object.")
        if set(data.keys()) != expected_keys:
            logger.warning("Bad json request. wanted=%s, got=%s", repr(expected_keys), repr(set(data.keys())))
            return HttpResponseBadRequest("Unexpected or Missing Fields.")

        data['issuedOn'] = datetime.datetime.fromtimestamp(data['issuedOn'])
        del data['action']

        obj = models.BadgeInstanceNotification.objects.create(**data)
        obj.full_clean() # throws ValidationError if fields are bad.
        obj.save()

        models.badge_instance_issued.send(obj, **data)
    except (ValueError, TypeError, ValidationError) as e:
        return HttpResponseBadRequest("Bad JSON request: %s" % str(e))

    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")


class InstanceListView(ListView):
    model = models.BadgeInstanceNotification


def create_claim_url(assertionUrl):
    return reverse('badgekit_webhooks.views.claim_page',
            args=[utils.encode_param(assertionUrl)])


def claim_page(request, b64_assertion_url):
    # The URL should be ASCII encoded: only IRIs use higher Unicode chars.  Right????
    assertionUrl = utils.decode_param(b64_assertion_url).decode('ascii')

    # TODO validate the URL against a whitelist

    return render(request, 'badgekit_webhooks/claim_page.html', {
        'assertionUrl': assertionUrl,
        'badge_image': utils.get_image_for_assertion(assertionUrl),
        })


# 'sender' here is a Django signal sender, not an e-mail sender.
def send_claim_email(sender, **kwargs):
    if not settings.BADGEKIT_SEND_CLAIM_EMAILS:
        logger.warning('Not sending e-mail to a badge earner, because settings.BADGEKIT_SEND_CLAIM_EMAILS is False')
        return

    logger.debug('Sending e-mail to a badge earner')
    context = {
            'claim_url': create_claim_url(smart_bytes(kwargs['assertionUrl'])),
            }
    context.update(kwargs)

    text_message = render_to_string('badgekit_webhooks/claim_email.txt', context)
    email = EmailMessage("You've earned a badge!", text_message,
            'from@example.com', [kwargs['email']])

    email.send()


models.badge_instance_issued.connect(send_claim_email, dispatch_uid='email-sender')
