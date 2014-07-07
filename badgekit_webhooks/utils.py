from __future__ import unicode_literals
import base64
import requests
import logging
from django.conf import settings
from urlparse import urlparse
from django.http import HttpResponseBadRequest
import json
import re

# From Django 1.6 - not present in 1.4.  django.utils.http.urlsafe_...
def urlsafe_base64_encode(s):
    """
    Encodes a bytestring in base64 for use in URLs, stripping any trailing
    equal signs.
    """
    return base64.urlsafe_b64encode(s).rstrip(b'\n=')


def urlsafe_base64_decode(s):
    """
    Decodes a base64 encoded string, adding back any trailing equal signs that
    might have been stripped.
    """
    s = s.encode('utf-8') # base64encode should only return ASCII.
    try:
        return base64.urlsafe_b64decode(s.ljust(len(s) + len(s) % 4, b'='))
    except (LookupError, BinasciiError) as e:
        raise ValueError(e)


decode_param = urlsafe_base64_decode
encode_param = urlsafe_base64_encode



def get_image_for_assertion(assertion_url):
    """
    Given a badge assertion URL, return an image for that assertion.

    If the assertion is not available or parseable, returns a default
    image, which is settings.BADGEKIT_DEFAULT_BADGE_IMAGE.
    """
    # Make sure assertion is one of the badges under the purview of this system
    if (test_whitelist_assertion_url(assertion_url)):
        pass
    
    else:
        return settings.BADGEKIT_DEFAULT_BADGE_IMAGE
    
    try:
        
        assertion_obj=get_assertion_properties(assertion_url)
        badge_property= assertion_obj['badge']
        if (badge_property== 'http://example.com/badge.json'):  #Test if its a URL
            badge_resp = requests.get(badge_property)
            badge_obj = json.loads(badge_resp.text) 
            return badge_obj['image']
    
        else:
            return badge_property['image']
        
        
    
    except (requests.exceptions.RequestException, ValueError, KeyError):
        logging.exception('Problem while determining image for assertion %s' % assertion_url)
        return settings.BADGEKIT_DEFAULT_BADGE_IMAGE

# def get_properties_for_assertion(assertion_url, props):
#     """
#     Given a badge assertion URL, return a specified list of properties for that assertion.

#     If the assertion is not available or parseable, returns a default
#     image, which is settings.BADGEKIT_DEFAULT_BADGE_IMAGE.
#     """
#     # TODO: make sure various URLs are subjected to a whitelist test.
#     # Maybe also check that they are reasonable size, etc?
#     try:
#         assertion_resp = requests.get(assertion_url)
#         assertion_obj = json.loads(assertion_resp.text)
#         badge_url = assertion_obj['badge']
#         badge_resp = requests.get(badge_url)
#         badge_obj = json.loads(badge_resp.text)
#         return badge_obj['image']

#     except (requests.exceptions.RequestException, ValueError, KeyError):
#         logging.exception('Problem while determining image for assertion %s' % assertion_url)
#         return settings.BADGEKIT_DEFAULT_BADGE_IMAGE

def test_whitelist_assertion_url(assertion_url):
    # For now, the only whitelisted site is the badgekit install
    whitelisturl = settings.BADGEKIT_API_URL
    parseofwhitelisturl = urlparse(whitelisturl)

    parseofassertionurl = urlparse(assertion_url)

    if((parseofassertionurl.scheme == parseofwhitelisturl.scheme) and (parseofassertionurl.netloc == parseofwhitelisturl.netloc)):
        return True
    else:
        return False  


def get_assertion_properties(assertion_url):

    assertion_resp= requests.get(assertion_url)
    assertion_obj=json.loads(assertion_resp.text)
    return assertion_obj
    



    

    

    




    

    






        