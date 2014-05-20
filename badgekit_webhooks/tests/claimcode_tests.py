from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import httpretty
import re
import json
from badgekit_webhooks import claimcode_views
from badgekit_webhooks import models


badge_list = {
        'badges': [
            { 'slug': 'one', 'name': 'One' }
            ]
        }


class IssuePageTest(TestCase):
    def setUp(self):
        if not User.objects.create_superuser('test', 'test@example.com', 'test1'):
            raise Exception("WTF no users")

    @httpretty.activate
    def testCanGetIssuePage(self):
        # Mock the badge list
        httpretty.register_uri(httpretty.GET,
                re.compile(r'example.com/.*'),
                body=json.dumps(badge_list))

        with self.settings(BADGEKIT_API_URL="http://example.com/",
                BADGEKIT_API_KEY="secret",
                BADGEKIT_SYSTEM='bk'):
            self.assertTrue(self.client.login(username='test', password='test1'))

            url = reverse('badge_issue_form')
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertTemplateUsed(resp, 'badgekit_webhooks/send_claim_code.html')

    def testGracefulNoBadgeAPI(self):
        with self.settings(BADGEKIT_API_URL="http://257.0.0.0/", # bad IP address
                BADGEKIT_API_KEY="secret",
                BADGEKIT_SYSTEM='bk'):
            self.assertTrue(self.client.login(username='test', password='test1'))

            url = reverse('badge_issue_form')
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 503)
            self.assertTemplateUsed(resp, 'badgekit_webhooks/badgekit_error.html')
            self.assertTrue('connection' in resp.content.decode('utf-8').lower())

    @httpretty.activate
    def testGracefulBadBadgeAPI(self):
        # Mock the badge list: invalidly this time
        httpretty.register_uri(httpretty.GET,
                re.compile(r'example.com/.*'),
                body="LULZ nope")

        with self.settings(BADGEKIT_API_URL="http://example.com/",
                BADGEKIT_API_KEY="secret",
                BADGEKIT_SYSTEM='bk'):
            self.assertTrue(self.client.login(username='test', password='test1'))

            url = reverse('badge_issue_form')
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 503)
            self.assertTemplateUsed(resp, 'badgekit_webhooks/badgekit_error.html')
            self.assertTrue('json' in resp.content.decode('utf-8').lower())


class ClaimPageTest(TestCase):
    badgekit_api_get_claimcode_response = {
                    'claimCode': {'claimed': False,
                        'code': '6f1c2410dc',
                        'email': 'so2me@example.com',
                        'id': 6,
                        'multiuse': False},
                    'badge': {'archived': False,
                        # much abbreviated
                        'imageUrl': 'http://localhost:3000/images/badge/2',
                        'name': 'Excellent Badge',
                        'slug': 'excellent-badge'},
                    }

    def testReverseUrl(self):
        url = reverse('claimcode_claim', args=['abc1234d'])

    def testGracefulBadClaimCode(self):
        with self.settings(BADGEKIT_API_URL="http://example.com/",
                BADGEKIT_API_KEY="secret",
                BADGEKIT_SYSTEM='bk'):
            # we don't create the object
            url = reverse('claimcode_claim', args=['nonexistant-code'])
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 404);

    def testGracefulNoBKAPI(self):
        with self.settings(BADGEKIT_API_URL="http://257.0.0.0/", # bad IP
                BADGEKIT_API_KEY="secret",
                BADGEKIT_SYSTEM='bk'):
            obj, created = models.ClaimCode.objects.get_or_create(
                    badge='excellent-badge',
                    code='6f1c2410dc',
                    system='badgekit', initial_email='so2me@example.com')
            self.assertTrue(obj)
            url = reverse('claimcode_claim', args=['6f1c2410dc'])
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 503);

    @httpretty.activate
    def testSuccessfulGet(self):
        httpretty.register_uri(httpretty.GET,
                re.compile(r'example.com/.*'),
                body=json.dumps(self.badgekit_api_get_claimcode_response))

        with self.settings(BADGEKIT_API_URL="http://example.com/",
                BADGEKIT_API_KEY="secret",
                BADGEKIT_SYSTEM='bk'):
            obj, created = models.ClaimCode.objects.get_or_create(
                    badge='excellent-badge',
                    code='6f1c2410dc',
                    system='badgekit', initial_email='so2me@example.com')
            self.assertTrue(obj)
            url = reverse('claimcode_claim', args=['6f1c2410dc'])
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200);
            self.assertTemplateUsed(resp, 'badgekit_webhooks/claim_code_claim.html')
