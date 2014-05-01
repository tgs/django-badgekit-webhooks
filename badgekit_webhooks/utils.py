import base64
import requests
from django.conf import settings


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
    "Given a badge assertion URL, return an image for that assertion."
    return settings.BADGEKIT_DEFAULT_BADGE_IMAGE
