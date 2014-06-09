from __future__ import unicode_literals
import re
from django.conf import settings
import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
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
from django.contrib.admin.views.decorators import staff_member_required

from .claimcode_views import *


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
        if type(data) != dict:
            logger.warning('Webhook request was valid JSON, but not an object. ???')
            return HttpResponseBadRequest("Not a JSON object.")

        if data['action'] != 'award':
            # we don't do anything yet with other actions.
            return HttpResponse(json.dumps({'status': "ok but I didn't do anything"}),
                    content_type="application/json")

        needed_keys = set(['uid', 'email', 'assertionUrl', 'issuedOn'])
        got_keys = set(data.keys())
        missing_keys = needed_keys - got_keys
        if missing_keys:
            logger.warning('Missing necessary keys from webhook: %s', repr(missing_keys))
            return HttpResponseBadRequest("Missing required JSON field(s).")

        data['issuedOn'] = datetime.datetime.fromtimestamp(data['issuedOn'])

        obj = models.BadgeInstanceNotification()
        for key in needed_keys:
            setattr(obj, key, data[key])
        obj.full_clean() # throws ValidationError if fields are bad.
        obj.save()

        models.badge_instance_issued.send(request, **data)
    except (ValueError, KeyError, TypeError, ValidationError) as e:
        logging.exception("Webhook: bad JSON request.")
        return HttpResponseBadRequest("Bad JSON request: %s" % str(e))

    return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")


class InstanceListView(ListView):
    model = models.BadgeInstanceNotification


def create_claim_url(assertionUrl):
    "Creates a RELATIVE URL.  You could use request.build_absolute_uri() then."
    return reverse('badgekit_webhooks.views.claim_page',
            args=[utils.encode_param(assertionUrl)])


# VIEW: a page for the user to claim a badge on the Backpack
def claim_page(request, b64_assertion_url):
    # The URL should be ASCII encoded: only IRIs use higher Unicode chars.  Right????
    assertionUrl = utils.decode_param(b64_assertion_url).decode('ascii')

    # TODO validate the URL against a whitelist

    api = models.get_badgekit_api()
    assertion = api.get_public_url(assertionUrl)
    badge = api.get_public_url(assertion['badge'])
    issuer = api.get_public_url(badge['issuer'])

    return render(request, 'badgekit_webhooks/claim_page.html', {
        'badge': badge,
        'assertion': assertion,
        'issuer': issuer,
        'assertionUrl': assertionUrl,
        })


@staff_member_required
def show_claim_email(request, b64_assertion_url, kind):
    assertionUrl = utils.decode_param(b64_assertion_url).decode('ascii')

    email_formats = render_claim_email(request, assertionUrl)
    if kind == 'html':
        return HttpResponse(email_formats[1])
    else:
        return HttpResponse(email_formats[0])

def render_claim_email(request, assertionUrl):
    abs_url = request.build_absolute_uri(
            create_claim_url(smart_bytes(assertionUrl)))

    site_base_url = request.build_absolute_uri('/')

    api = models.get_badgekit_api()
    assertion = api.get_public_url(assertionUrl)
    badge = api.get_public_url(assertion['badge'])
    issuer = api.get_public_url(badge['issuer'])

    context = {
            'claim_url': abs_url,
            'assertionUrl': assertionUrl,
            'assertion': assertion,
            'badge': badge,
            'issuer': issuer,
            # TODO: this could come from BKAPI, but we only have the 'public'
            # urls of the badge information.  We would have to get the same
            # url, but with /public/ removed from the beginning.
            'badge_earner_description': 'Contribute to the edX code, which is accomplished most visibly with an accepted pull request on GitHub. The link below WILL NOT WORK, this is coming from my localhost. But check out how responsive this email template is by resizing your viewing window! So response!',
            'site_base_url': site_base_url,
            'unsubscribe_link': '#',
            }

    text_message = render_to_string(
            'badgekit_webhooks/claim_email.txt', context)
    html_message = render_to_string(
            'badgekit_webhooks/badge_earned_email.html', context)

    return (text_message, html_message)


# 'sender' here is a Django signal sender, not an e-mail sender.
# In this case, it must be a Django Request object.
def send_claim_email(sender, **kwargs):
    if not settings.BADGEKIT_SEND_CLAIM_EMAILS:
        logger.warning('Not sending e-mail to a badge earner, because settings.BADGEKIT_SEND_CLAIM_EMAILS is False')
        return

    logger.info('Sending e-mail to badge earner %s', kwargs['email'])

    text_message, html_message = render_claim_email(
            sender, kwargs['assertionUrl'])

    email = EmailMultiAlternatives(
            "You've earned a badge!",
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [kwargs['email']])
    email.attach_alternative(html_message, "text/html")
    email.send()


models.badge_instance_issued.connect(send_claim_email, dispatch_uid='email-sender')

def list_badges_view(request):
    context = {
        'badge_list': models.Badge.list_badges()
        }
    return render(request, 'badgekit_webhooks/badge_list.html', context)
