from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import reverse
import json
import jwt
import hashlib
import contextlib


from .claim_tests import *


class Tests(TestCase):
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


class CatchingSignal(object):
    def __init__(self, signal):
        self._signal = signal
        self.caught = False
        self.sender = None
        self.kwargs = None

    def __enter__(self):
        self._signal.connect(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._signal.disconnect(self)

    # Called by the signal dispatcher
    def __call__(self, sender, **kwargs):
        self.caught = True
        self.sender = sender
        self.kwargs = kwargs


class CatchingSignalTestTestTest(TestCase):
    def testCanCatch(self):
        import django.dispatch
        sig = django.dispatch.Signal(providing_args=['nifty'])
        with CatchingSignal(sig) as catcher:
            sig.send(self, nifty="bill gates")
            self.assertTrue(catcher.caught)
            self.assertEqual(catcher.kwargs['nifty'], 'bill gates')
            self.assertIs(catcher.sender, self)


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

    def testNoBodySig(self):
        key = 'JWT key for testing'
        with self.settings(BADGEKIT_JWT_KEY=key):
            resp = self.client.post(hook_url,
                    data=hook_demo_data,
                    content_type="application/json",
                    HTTP_AUTHORIZATION=(
                        'JWT token="%s"' % jwt.encode({'something': 'hi'}, key=key)))
            self.assertEqual(resp.status_code, 403)

    def testSuccess(self):
        key = 'JWT key for testing'
        with self.settings(BADGEKIT_JWT_KEY=key):
            resp = self.client.post(hook_url,
                    data=hook_demo_data,
                    content_type="application/json",
                    HTTP_AUTHORIZATION=(
                        'JWT token="%s"' % jwt.encode(
                        {
                            'body': {
                                'alg': 'sha256',
                                'hash': hashlib.sha256(
                                    hook_demo_data.encode('utf-8')).hexdigest(),
                        }}, key=key)))
            self.assertEqual(resp.status_code, 200)


class SignalTest(TestCase):
    def testSignalIsSent(self):
        from badgekit_webhooks.models import badge_instance_issued
        with self.settings(BADGEKIT_SKIP_JWT_AUTH=True):
            with CatchingSignal(badge_instance_issued) as catcher:
                self.client.post(hook_url,
                        data=hook_demo_data,
                        content_type="application/json")
                self.assertTrue(catcher.caught)
                self.assertEqual(catcher.kwargs['email'], 'awardee@example.com')
                self.assertEqual(catcher.kwargs['assertionUrl'], "http://example.com/assertion/asdf1234")
