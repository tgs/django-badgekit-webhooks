from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import reverse
import json
import jwt
import hashlib
import contextlib
import httpretty
import re

from badgekit_webhooks import views

badge_info_dummy = {
        'badge': 'http://example.com/badge',
        'issuer': 'http://example.com/issuer',
        'url': 'http://example.com/blah',
        'image': 'http://example.com/img',
        }

def register_dummy():
    httpretty.register_uri(httpretty.GET,
            re.compile(r'evil.com/.*'),
            body=json.dumps(badge_info_dummy))
    httpretty.register_uri(httpretty.GET,
            re.compile(r'example.com/.*'),
            body=json.dumps(badge_info_dummy))


class ClaimPageTest(TestCase):
    @httpretty.activate
    def testCanGetClaimPage(self):
        register_dummy()
        url = views.create_claim_url(b'http://example.com/assertion.json')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    @httpretty.activate
    def testQuotesDoNotAppear(self):
        register_dummy()
        url = views.create_claim_url(b'http://evil.com/quote"quote')
        resp = self.client.get(url)
        self.assertFalse(b'quote"quote' in resp.content)

    @httpretty.activate
    def testBracketsDoNotAppear(self):
        register_dummy()
        url = views.create_claim_url(b"http://evil.com/angle<angle>angle")
        resp = self.client.get(url)
        self.assertFalse(b"angle<" in resp.content)
        self.assertFalse(b"angle>" in resp.content)

    @httpretty.activate
    def testMoreChars(self):
        register_dummy()
        url = views.create_claim_url(b"http://evil.com/semi;dquote\"")
        resp = self.client.get(url)
        self.assertFalse(b'dquote"' in resp.content)
