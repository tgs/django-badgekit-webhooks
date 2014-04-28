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
        url = views.create_claim_url(b'http://example.com/assertion.json')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def testQuotesDoNotAppear(self):
        url = views.create_claim_url(b"http://evil.com/quote'quote")
        resp = self.client.get(url)
        self.assertFalse(b"quote'quote" in resp.content)
        self.assertFalse(b"quote&#39;quote" in resp.content)

    def testBracketsDoNotAppear(self):
        url = views.create_claim_url(b"http://evil.com/angle<angle>angle")
        resp = self.client.get(url)
        self.assertFalse(b"angle<" in resp.content)
        self.assertFalse(b"angle>" in resp.content)

    def testMoreChars(self):
        url = views.create_claim_url(b"http://evil.com/semi;dquote\"")
        resp = self.client.get(url)
        self.assertFalse(b'semi;' in resp.content)
        self.assertFalse(b'dquote"' in resp.content)
