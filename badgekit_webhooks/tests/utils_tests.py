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

    #@httpretty.activate
    #def testGoodAssertion(self):
        #default_url = 'http://example.com/no.gophers.png'
        #good_url = 'https://example.org/robotics-badge.png'
        #with self.settings(BADGEKIT_DEFAULT_BADGE_IMAGE=default_url):
            #   httpretty.register_uri(httpretty.GET,
            #          re.compile('example.com/assertion'),
            #         body=json.dumps({
            #            'badge': 'http://example.com/badge.json',
            #           }))
            #httpretty.register_uri(httpretty.GET,
            #       re.compile('example.com/badge'),
            #      body=json.dumps({
            #         'image': good_url,
            #            }))
        #url = utils.get_image_for_assertion('http://example.com/assertion.json')

        #self.assertEqual(url, good_url)

   
        
    @httpretty.activate
    def testassertion_properties_badgeURL(self):
        
        httpretty.register_uri(httpretty.GET,
                    re.compile('example.com/assertion'),
                    body=json.dumps({

                        'uid': 12435,
                        'recipient':'test@test.com',
                        'badge': 'http://example.com/badge.json',
                        'issuedOn':'1359217910'
                    
                        }))
        httpretty.register_uri(httpretty.GET,
                    re.compile('example.com/badge'),
                    body=json.dumps({
                        "name": "Awesome Robotics Badge",
                        "description": "For doing awesome things with robots that people think is pretty great.",
                        "image": "https://example.org/robotics-badge.png",
                        "criteria": "https://example.org/robotics-badge.html",
                        "tags": ["robots", "awesome"],
                        "issuer": "https://example.org/organization.json",
                        "alignment":[
                            {   "name": "CCSS.ELA-Literacy.RST.11-12.3",
                                "url": "http://www.corestandards.org/ELA-Literacy/RST/11-12/3",
                                "description": "Follow precisely a complex multistep procedure when carrying out experiments, taking measurements, or performing technical tasks; analyze the specific results based on explanations in the text."
                            },
                            { 
                                "name": "CCSS.ELA-Literacy.RST.11-12.9",
                                "url": "http://www.corestandards.org/ELA-Literacy/RST/11-12/9",
                                "description": " Synthesize information from a range of sources (e.g., texts, experiments, simulations) into a coherent understanding of a process, phenomenon, or concept, resolving conflicting information when possible."
                            }
                          ]
                       }))
       
        url=utils.get_image_for_assertion('http://example.com/assertion.json')
        self.assertEqual(url,'https://example.org/robotics-badge.png')

    @httpretty.activate
    def testassertion_properties_badgeobj(self):
        
        httpretty.register_uri(httpretty.GET,
                    re.compile('example.com/assertion'),
                    body=json.dumps({
                        
                        'uid': 12435,
                        'recipient':'test@test.com',
                        'badge': {
                        "name": "Awesome Robotics Badge",
                        "description": "For doing awesome things with robots that people think is pretty great.",
                        "image": "https://example.org/robotics-badge.png",
                        "criteria": "https://example.org/robotics-badge.html",
                        "tags": ["robots", "awesome"],
                        "issuer": "https://example.org/organization.json",
                        "alignment":[
                            {   "name": "CCSS.ELA-Literacy.RST.11-12.3",
                                "url": "http://www.corestandards.org/ELA-Literacy/RST/11-12/3",
                                "description": "Follow precisely a complex multistep procedure when carrying out experiments, taking measurements, or performing technical tasks; analyze the specific results based on explanations in the text."
                            },
                            { 
                                "name": "CCSS.ELA-Literacy.RST.11-12.9",
                                "url": "http://www.corestandards.org/ELA-Literacy/RST/11-12/9",
                                "description": " Synthesize information from a range of sources (e.g., texts, experiments, simulations) into a coherent understanding of a process, phenomenon, or concept, resolving conflicting information when possible."
                            }
                          ]
                        },
                        'issuedOn':'1359217910'

                        }))

        url=utils.get_image_for_assertion('http://example.com/assertion.json')
        self.assertEqual(url,'https://example.org/robotics-badge.png')

        
   
        
       
        
       











