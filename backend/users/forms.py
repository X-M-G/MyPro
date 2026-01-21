from django import forms
from django.utils.translation import gettext_lazy as _

class AddCreditsForm(forms.Form):
    amount = forms.IntegerField(
        label=_('Credit Amount'),
        help_text=_('Positive to add, negative to deduct'),
        widget=forms.NumberInput(attrs={'step': 1})
    )
    description = forms.CharField(
        label=_('Description'),
        required=True,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text=_('Reason for the credit change')
    )
