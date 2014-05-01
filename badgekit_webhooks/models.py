from __future__ import unicode_literals
from django.db import models
import django.dispatch
from appconf import AppConf
from django.templatetags.static import static


class BadgekitWebhooksAppConf(AppConf):
    SKIP_JWT_AUTH = False
    JWT_KEY = None
    SEND_CLAIM_EMAILS = False
    DEFAULT_BADGE_IMAGE = static('badgekit_webhooks/default_badge.png')

    class Meta:
        prefix = 'badgekit'


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
