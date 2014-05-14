from __future__ import unicode_literals
from django.views.generic.edit import FormMixin
from django.views.generic.base import View, TemplateResponseMixin
from .forms import SendClaimCodeForm
from .models import Badge

# This view starts as a copy of django.views.generic.edit.ProcessFormView
class SendClaimCodeView(TemplateResponseMixin, FormMixin, View):
    template_name = 'badgekit_webhooks/send_claim_code.html'
    form_class = SendClaimCodeForm
    success_url = '/' # TODO

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def form_valid(self, form):
        self.send_claim_mail(form)
        return super(SendClaimCodeView, self).form_valid(form)

    def send_claim_mail(self, form):
        # if the code doesn't work, tell the admin so?
        code = Badge.create_claim_code(
                form.cleaned_data['badge'],
                form.cleaned_data['awardee'])
        print(code)
        # TODO: send the code in an email, etc.
