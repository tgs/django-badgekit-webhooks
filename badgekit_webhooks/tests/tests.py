from django.test import TestCase
from django.core.urlresolvers import reverse


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
    "issuedOn": "TODO how is this encoded"
}
'''

hook_url = reverse('badge_issued_hook')

class HookTests(TestCase):
    def testCanPost(self):
        resp = self.client.post(hook_url)
        self.assertNotEqual(resp.status_code, 405)

    def testCannotGet(self):
        resp = self.client.get(hook_url)
        self.assertEqual(resp.status_code, 405)

    def testRejectNonJSON(self):
        resp = self.client.post(hook_url,
                data=u'!this is { not good json data%',
                content_type="application/json")
        self.assertNotEqual(resp.status_code, 200)

    def testGoodRequest(self):
        resp = self.client.post(hook_url,
                data=hook_demo_data,
                content_type="application/json")
        self.assertEqual(resp.status_code, 200)
