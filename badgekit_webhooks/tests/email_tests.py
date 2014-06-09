from __future__ import unicode_literals
from badgekit_webhooks import utils
from django.test import TestCase
from badgekit_webhooks import views
from badgekit_webhooks import models
from django.core import mail
import datetime
import httpretty
import json
import re


badge_info_dummy = {
        'badge': 'http://example.com/badge',
        'issuer': 'http://example.com/issuer',
        'url': 'http://example.com/blah',
        'image': 'http://example.com/img',
        }


def register_dummy():
    httpretty.register_uri(httpretty.GET,
            re.compile(r'example.com/.*'),
            body=json.dumps(badge_info_dummy))


class MockRequest(object):
    def build_absolute_uri(self, location):
        return "http://example.com/Fake-absolute-uri"


class SendEmailTest(TestCase):
    @httpretty.activate
    def testEmailIsSent(self):
        register_dummy()
        # Need DEBUG=True because django-inlinecss depends on it >_<
        with self.settings(BADGEKIT_SEND_CLAIM_EMAILS=True, DEBUG=True):
            models.badge_instance_issued.send(sender=MockRequest(),
                    uid='asdf1234', email='recipient@example.com',
                    assertionUrl='http://example.com/assertion/1.json',
                    issuedOn=datetime.datetime.now())

            self.assertEqual(len(mail.outbox), 1)
