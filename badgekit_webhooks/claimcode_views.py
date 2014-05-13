from __future__ import unicode_literals
from django.views.generic.edit import FormView
from .forms import SendClaimCodeForm

class SendClaimCodeView(FormView):
    template_name = 'badgekit_webhooks/send_claim_code.html'
    form_class = SendClaimCodeForm
    success_url = '/' # TODO

    def form_valid(self, form):
        return super(SendClaimCodeView, self).form_valid(form)
