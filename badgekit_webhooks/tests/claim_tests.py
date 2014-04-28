from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import reverse
import json
import jwt
import hashlib
import contextlib

from badgekit_webhooks import views


class ClaimPageTest(TestCase):
    def testCanGetClaimPage(self):
        url = views.create_claim_url('http://example.com/assertion.json')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
