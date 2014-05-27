from __future__ import unicode_literals
from django.views.generic.edit import FormMixin
from django.views.generic.edit import FormView
from django.views.generic.base import View, TemplateResponseMixin
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from . import forms
from .models import Badge, ClaimCode
from badgekit import RequestException, BadgeKitException
from django.contrib.admin.views.decorators import staff_member_required
import logging as __logging

logger = __logging.getLogger(__name__)


def render_badgekit_error(request, exception, message=None):
    logger.warning("Problem with badgekit: %s" % exception)
    return render(request,
            'badgekit_webhooks/badgekit_error.html',
            {
                'exception': exception,
                'message': message,
            },
            status=503)


# This view starts as a copy of django.views.generic.edit.ProcessFormView
class SendClaimCodeView(TemplateResponseMixin, FormMixin, View):
    template_name = 'badgekit_webhooks/send_claim_code.html'
    form_class = forms.SendClaimCodeForm
    success_url = '/' # TODO

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        try:
            form.fields['badge'].choices = self.get_badge_choices()
            return self.render_to_response(self.get_context_data(form=form))
        except (RequestException, BadgeKitException) as e:
            return render_badgekit_error(request, e)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        try:
            form.fields['badge'].choices = self.get_badge_choices()
        except (RequestException, BadgeKitException) as e:
            return render_badgekit_error(request, e,
                    message='No e-mail was sent.')

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def get_badge_choices(self):
        return Badge.form_choices()

    def form_valid(self, form, request):
        try:
            code_obj = ClaimCode.create(
                badge=form.cleaned_data['badge'],
                initial_email=form.cleaned_data['awardee'])
            self.send_claim_mail(request, code_obj)
        except (RequestException, BadgeKitException) as e:
            return render_badgekit_error(request, e)

        return super(SendClaimCodeView, self).form_valid(form)

    def send_claim_mail(self, request, code_obj):
        claim_url = request.build_absolute_uri(
                reverse('claimcode_claim', args=[code_obj.code]))
        context = {
            'claim_url': claim_url,
            'organization': 'open edX',
            'badge_name': 'Open edX Contributor',
            'badgeclass_image_url': 'http://placekitten.com/300/300',
            'badge_earner_description': 'Contribute to the edX code, which is accomplished most visibly with an accepted pull request on GitHub.',
            'about_program_url': '#',
            'contact_email': 'contact@example.com',
            'site_base_url': 'http://localhost:8000',
            'unsubscribe_link': '#',
            }

        text_message = render_to_string('badgekit_webhooks/claim_code_email.txt', context)
        html_message = render_to_string('badgekit_webhooks/claim_code_email.html')

        email = EmailMultiAlternatives("You've earned a badge!", text_message,
            settings.DEFAULT_FROM_EMAIL, [code_obj.initial_email])
        email.attach_alternative(html_message, "text/html")
        email.send()


class ClaimCodeClaimView(View):
    template_name = 'badgekit_webhooks/claim_code_claim.html'
    form_class = forms.ClaimCodeClaimForm
    success_url = '/' # TODO

    def get(self, request, *args, **kwargs):
        code = args[0]

        try:
            claim_obj = ClaimCode.objects.get(code=code)
        except ClaimCode.DoesNotExist:
            return render(request, "badgekit_webhooks/claim_code_404.html", {},
                    status=404)

        try:
            api_info = claim_obj.get_info()
        except (BadgeKitException, RequestException) as e:
            return render_badgekit_error(request, e)

        already_claimed = api_info['claimCode']['claimed']
        # if already claimed, then... TODO
        return render(request, self.template_name, {'asdf': 'Jkl'})
