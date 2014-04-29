from __future__ import unicode_literals
from django.test import TestCase
from badgekit_webhooks import views
from badgekit_webhooks import models
from django.core import mail
import datetime


class SendEmailTest(TestCase):
    def testEmailIsSent(self):
        with self.settings(BADGEKIT_SEND_CLAIM_EMAILS=True):
            models.badge_instance_issued.send(sender=self,
                    uid='asdf1234', email='recipient@example.com',
                    assertionUrl='http://example.com/assertion/1.json',
                    issuedOn=datetime.datetime.now())

            self.assertEqual(len(mail.outbox), 1)
