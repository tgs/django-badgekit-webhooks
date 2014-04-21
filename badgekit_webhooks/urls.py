from django.conf.urls import patterns, url


urlpatterns = patterns(
    "",
    url(r"^hello/$", "badgekit_webhooks.views.hello", name="badgekit_webhooks_hello"),
    )
