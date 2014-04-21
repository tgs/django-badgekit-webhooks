from django.test import TestCase


class Tests(TestCase):

    def setUp(self):
        pass

    # this is an integration test, not a unit test, but...
    def testHello(self):
        resp = self.client.get('/hello/')
        self.assertEqual(resp.status_code, 200)
