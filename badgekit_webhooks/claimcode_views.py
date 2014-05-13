from __future__ import unicode_literals
from django.views.generic.edit import FormView
from .forms import SendClaimCodeForm
from .models import Badge

class SendClaimCodeView(FormView):
    template_name = 'badgekit_webhooks/send_claim_code.html'
    form_class = SendClaimCodeForm
    success_url = '/' # TODO

    def form_valid(self, form):
        self.send_claim_mail(form)
        return super(SendClaimCodeView, self).form_valid(form)

    def send_claim_mail(self, form):
        code = Badge.create_claim_code(
                form.cleaned_data['badge'],
                form.cleaned_data['awardee'])
        print(code)
        # TODO: send the code in an email, etc.
