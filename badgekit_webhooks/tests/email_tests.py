from __future__ import unicode_literals
from badgekit_webhooks import utils
from django.test import TestCase
from badgekit_webhooks import views
from badgekit_webhooks import models
from django.core import mail
import datetime


class MockRequest(object):
    def build_absolute_uri(self, location):
        return "Fake-absolute-uri"


class SendEmailTest(TestCase):
    def setUp(self):
        # monkey patch / mock the image grabber
        self.old_get_image = utils.get_image_for_assertion
        utils.get_image_for_assertion = lambda x: 'http://example.com/image.png'

    def testEmailIsSent(self):
        # Need DEBUG=True because django-inlinecss depends on it >_<
        with self.settings(BADGEKIT_SEND_CLAIM_EMAILS=True, DEBUG=True):
            models.badge_instance_issued.send(sender=MockRequest(),
                    uid='asdf1234', email='recipient@example.com',
                    assertionUrl='http://example.com/assertion/1.json',
                    issuedOn=datetime.datetime.now())

            self.assertEqual(len(mail.outbox), 1)

    def tearDown(self):
        utils.get_image_for_assertion = self.old_get_image
