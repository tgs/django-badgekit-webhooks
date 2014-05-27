from django import forms


class SendClaimCodeForm(forms.Form):
    badge = forms.ChoiceField(choices=[])
    awardee = forms.EmailField()


class ClaimCodeClaimForm(forms.Form):
    # include claimcode?  It's in the URL, so ...
    issue_email = forms.EmailField()
