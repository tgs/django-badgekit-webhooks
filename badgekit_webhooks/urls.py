from __future__ import unicode_literals
from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns(
    "",
    url(r"^hello/$", "badgekit_webhooks.views.hello", name="badgekit_webhooks_hello"),
    url(r"^issued/$", "badgekit_webhooks.views.badge_issued_hook",
        name="badge_issued_hook"),
    url(r"^instances/$", views.InstanceListView.as_view()),
    )
