from __future__ import unicode_literals
from django.conf.urls import patterns, url
from . import views
from django.contrib.admin.views.decorators import staff_member_required


urlpatterns = patterns(
    "",
    url(r"^hello/$", "badgekit_webhooks.views.hello", name="badgekit_webhooks_hello"),
    url(r"^issued/$", "badgekit_webhooks.views.badge_issued_hook",
        name="badge_issued_hook"),
    url(r"^instances/$", views.InstanceListView.as_view()),
    url(r"^claim/([-A-Za-z0-9_]+)/$", 'badgekit_webhooks.views.claim_page'),
    url(r"^claim/([-A-Za-z0-9_]+)/email/(html|text)$", 'badgekit_webhooks.views.show_claim_email',
        name="show_claim_email"),
    url(r"^issue/$", staff_member_required(views.SendClaimCodeView.as_view()),
        name="badge_issue_form"),
    url(r"^claimcode/([-A-Za-z.0-9_]+)/$",
        views.ClaimCodeClaimView.as_view(), name='claimcode_claim'),
    url(r"^badges/$", "badgekit_webhooks.views.list_badges_view", name="badges_list"),
    )
