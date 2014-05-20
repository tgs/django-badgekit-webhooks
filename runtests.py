#!/usr/bin/env python
import os
import sys

import django

from django.conf import settings


DEFAULT_SETTINGS = dict(
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sites",
        "django.contrib.staticfiles",
        "django_nose",
        "django_inlinecss",
        "badgekit_webhooks",
        "badgekit_webhooks.tests"
    ],
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    STATIC_URL="/static/",
    STATIC_ROOT="staticfiles",
    SITE_ID=1,
    ROOT_URLCONF="badgekit_webhooks.tests.urls",
    SECRET_KEY="notasecret",
)


def runtests(*test_args):
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)

    # Allow AppConf to inject its settings
    import badgekit_webhooks.models
    # Compatibility with Django 1.7's stricter initialization
    if hasattr(django, "setup"):
        django.setup()

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)
    settings.TEMPLATE_DIRS = settings.TEMPLATE_DIRS + (
            os.path.join(parent, 'badgekit_webhooks/tests/templates'),
            )

    from django_nose import NoseTestSuiteRunner as TestRunner

    failures = TestRunner(
        verbosity=1, interactive=True, failfast=False).run_tests(test_args)
    sys.exit(failures)


if __name__ == "__main__":
    runtests(*sys.argv[1:])
