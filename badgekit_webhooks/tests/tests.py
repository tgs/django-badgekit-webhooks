from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import reverse
import json


class Tests(TestCase):

    def setUp(self):
        pass

    # this is an integration test, not a unit test, but...
    def testHello(self):
        resp = self.client.get('/hello/')
        self.assertEqual(resp.status_code, 200)

hook_demo_data = '''{
    "action": "award",
    "uid": "asdf1234",
    "email": "awardee@example.com",
    "assertionUrl": "http://example.com/assertion/asdf1234",
    "issuedOn": 1398183058
}
'''
hook_demo_obj = json.loads(hook_demo_data)

hook_url = reverse('badge_issued_hook')


class HookTests(TestCase):
    def testCanPost(self):
        with self.settings(BADGEKIT_SKIP_JWT_AUTH=True):
            resp = self.client.post(hook_url)
            self.assertNotEqual(resp.status_code, 405)

    def testCannotGet(self):
        with self.settings(BADGEKIT_SKIP_JWT_AUTH=True):
            resp = self.client.get(hook_url)
            self.assertEqual(resp.status_code, 405)

    def testRejectNonJSON(self):
        with self.settings(BADGEKIT_SKIP_JWT_AUTH=True):
            resp = self.client.post(hook_url,
                        data='!this is { not good json data%',
                        content_type="application/json")
            self.assertEqual(resp.status_code, 400)

    def testGoodRequest(self):
        with self.settings(BADGEKIT_SKIP_JWT_AUTH=True):
            resp = self.client.post(hook_url,
                        data=hook_demo_data,
                        content_type="application/json")
            self.assertEqual(resp.status_code, 200)

    def testRejectBadFields(self):
        with self.settings(BADGEKIT_SKIP_JWT_AUTH=True):
            resp = self.client.post(hook_url,
                    data='{"uid": "jkjkjkj", "devilishField": 1234}',
                    content_type="application/json")
            self.assertEqual(resp.status_code, 400)

    def testRejectValidJSONButNotDict(self):
        with self.settings(BADGEKIT_SKIP_JWT_AUTH=True):
            resp = self.client.post(hook_url,
                    data='[]',
                    content_type="application/json")
            self.assertEqual(resp.status_code, 400)

    def testRejectInvalidEmail(self):
        with self.settings(BADGEKIT_SKIP_JWT_AUTH=True):
            data = dict(**hook_demo_obj)
            data['email'] = 'This sentence has two erors and is not an email.'
            resp = self.client.post(hook_url,
                    data=json.dumps(data),
                    content_type="application/json")
            self.assertEqual(resp.status_code, 400)

    def testRejectInvalidDate(self):
        with self.settings(BADGEKIT_SKIP_JWT_AUTH=True):
            data = dict(**hook_demo_obj)
            data['issuedOn'] = 'This sentence has two erors and is not a date.'
            resp = self.client.post(hook_url,
                    data=json.dumps(data),
                    content_type="application/json")
            self.assertEqual(resp.status_code, 400)


class JWTTests(TestCase):
    def testRejectNoJWT(self):
        resp = self.client.post(hook_url,
                    data=hook_demo_data,
                    content_type="application/json")
        self.assertEqual(resp.status_code, 401)
