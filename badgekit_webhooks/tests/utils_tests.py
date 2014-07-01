from __future__ import unicode_literals
from badgekit_webhooks import utils
from django.test import TestCase
import httpretty
import json
import re


class ClaimImageTest(TestCase):
    def testBrokenAssertionURL(self):
        default_url = 'http://example.com/no.gophers.png'
        with self.settings(BADGEKIT_DEFAULT_BADGE_IMAGE=default_url):
            url = utils.get_image_for_assertion('gopher://bad.url')
            self.assertEqual(url, default_url)

    @httpretty.activate
    def testBrokenJSON(self):
        default_url = 'http://example.com/no.gophers.png'
        with self.settings(BADGEKIT_DEFAULT_BADGE_IMAGE=default_url):
            httpretty.register_uri(httpretty.GET,
                    re.compile('example.com/.*'),
                    body='!this ain\'t json')
            url = utils.get_image_for_assertion('http://example.com/assertion.json')

            self.assertEqual(url, default_url)
            req = httpretty.last_request()
            self.assertEqual(req.path, '/assertion.json')

    @httpretty.activate
    def testBrokenAssertion(self):
        default_url = 'http://example.com/no.gophers.png'
        with self.settings(BADGEKIT_DEFAULT_BADGE_IMAGE=default_url):
            httpretty.register_uri(httpretty.GET,
                    re.compile('example.com/.*'),
                    body=json.dumps({
                        'valid': 'Yes, good JSON, but not an assertion.',
                        }))
            url = utils.get_image_for_assertion('http://example.com/assertion.json')

            self.assertEqual(url, default_url)
            req = httpretty.last_request()
            self.assertEqual(req.path, '/assertion.json')

    @httpretty.activate
    def testGoodAssertion(self):
        default_url = 'http://example.com/no.gophers.png'
        good_url = 'http://example.com/correct-image.png'
        with self.settings(BADGEKIT_DEFAULT_BADGE_IMAGE=default_url):
            httpretty.register_uri(httpretty.GET,
                    re.compile('example.com/assertion'),
                    body=json.dumps({
                        'badge': 'http://example.com/badge.json',
                        }))
            httpretty.register_uri(httpretty.GET,
                    re.compile('example.com/badge'),
                    body=json.dumps({
                        'image': good_url,
                        }))
            url = utils.get_image_for_assertion('http://example.com/assertion.json')

            self.assertEqual(url, good_url)

    @httpretty.activate
    def testassertionproperties(self):
        
        httpretty.register_uri(httpretty.GET,
                    re.compile('example.com/assertion'),
                    body=json.dumps({
                        'uid': 12435,
                        'recipient':'test@test.com'
                
                        }))
        property_value1 = utils.get_assertion_properties('http://example.com/assertion.json','BADGE_ID')
        property_value2 = utils.get_assertion_properties('http://example.com/assertion.json','BADGE_RECIPIENT')
        
        
        #resp = self.client.get(url)
    
        #self.assertEqual(resp.status_code, 200)











