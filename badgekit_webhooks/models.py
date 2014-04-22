from __future__ import unicode_literals
from django.db import models


class BadgeInstanceNotification(models.Model):
    "Represents a badge instance that has been shown to us with a webhook."

    # TODO Should I set this as primary key?
    uid = models.CharField(max_length=255)
    # Is it smart to use validating fields for these bits?
    # Should I just use CharFields for each?
    email = models.EmailField(max_length=255)
    assertionUrl = models.URLField(max_length=255)
    issuedOn = models.DateTimeField(db_index=True)
