from django import forms
from .models import Badge


class SendClaimCodeForm(forms.Form):
    badge = forms.ChoiceField(choices=[])
    awardee = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(SendClaimCodeForm, self).__init__(*args, **kwargs)
        self.fields['badge'].choices = Badge.form_choices()
