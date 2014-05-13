from __future__ import unicode_literals
from django.db import models
import django.dispatch
from django.conf import settings
from appconf import AppConf
from django.templatetags.static import static
from badgekit.api import BadgeKitAPI


class BadgekitWebhooksAppConf(AppConf):
    """
    To set any of these settings in your project / site,
    put BADGEKIT_ at the beginning, and add it to your settings.py.

    For example, to set the JWT key, add this to settings.py:

        BADGEKIT_JWT_KEY = 'my key la la la'
    """

    SKIP_JWT_AUTH = False
    """
    Set to True to skip checking the Authorization header of incoming
    webhook requests.  Useful for testing, but obviously insecure!
    It would be pretty easy for an attacker to spam people if you turn
    on this setting.
    """

    JWT_KEY = None
    """
    The secret key used to authorize / authenticate the webhook
    requests.  In the BadgeKit-API's database, set the `secret`
    column in the `webhooks` table to this same value.  It does
    not need to be the same as the "master secret" used to
    communicate between OpenBadges-BadgeKit and BadgeKit-API!
    """

    SEND_CLAIM_EMAILS = settings.DEBUG
    """
    Send people who earn badges an e-mail asking them to claim them?

    Defaults to True if settings.DEBUG is True, False otherwise.  This is
    so that it's harder to shoot yourself in the foot.  You must explicitly
    enable sending e-mails in production before any will be sent.
    """

    DEFAULT_BADGE_IMAGE = static('badgekit_webhooks/default_badge.png')
    """
    This image is shown on the badge claim page if the real badge is inaccessible.
    """

    API_KEY = None
    """
    The secret key with which to sign requests to the
    BadgeKit API server.  This is probably the "master secret"
    from the environment of the server.
    """

    API_URL = None
    """
    The base URL of the BadgeKit API server.  For example, when
    testing, this might be `http://localhost:8080/`.
    """

    SYSTEM = None
    """
    The 'system' slug to use with the Badgekit API
    """

    ISSUER = None
    """
    The 'issuer' slug to use with the Badgekit API
    """

    PROGRAM = None
    "The 'program' slug to use with the Badgekit API"

    class Meta:
        prefix = 'badgekit'


_bkapi = BadgeKitAPI(settings.BADGEKIT_API_URL,
        settings.BADGEKIT_API_KEY)
_bkapi_kwargs = {
        'system': settings.BADGEKIT_SYSTEM,
        'issuer': settings.BADGEKIT_ISSUER,
        'program': settings.BADGEKIT_PROGRAM,
        }


class BadgeInstanceNotification(models.Model):
    "Represents a badge instance that has been shown to us with a webhook."

    # TODO Should I set this as primary key?
    uid = models.CharField(max_length=255)
    # Is it smart to use validating fields for these bits?
    # Should I just use CharFields for each?
    email = models.EmailField(max_length=255)
    assertionUrl = models.URLField(max_length=255)
    issuedOn = models.DateTimeField(db_index=True)


badge_instance_issued = django.dispatch.Signal(
        providing_args=['uid', 'email', 'assertionUrl', 'issuedOn'])


class Badge(object):
    @staticmethod
    def form_choices():
        badges = _bkapi.list('badge', **_bkapi_kwargs)
        return [(b['slug'], b['name']) for b in badges['badges']]

    @staticmethod
    def create_claim_code(badge_slug, email):
        response = _bkapi.create('codes/random', {'email': email},
                badge=badge_slug, **_bkapi_kwargs)
        return response['claimCode']['code']
