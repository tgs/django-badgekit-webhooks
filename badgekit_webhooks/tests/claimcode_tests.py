from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import httpretty
import re
import json


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
