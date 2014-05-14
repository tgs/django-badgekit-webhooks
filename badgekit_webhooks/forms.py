from django import forms


class SendClaimCodeForm(forms.Form):
    badge = forms.ChoiceField(choices=[])
    awardee = forms.EmailField()
