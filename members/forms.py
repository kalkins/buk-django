from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django import forms

from .models import *
from base.forms import BasePeriodFormset

class MemberAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'E-post'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Passord'}))


class MemberPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'E-post'}))


MembershipPeriodFormset = forms.inlineformset_factory(
    Member,
    MembershipPeriod,
    formset = BasePeriodFormset,
    extra = 1,
    fields = ('start', 'end'),
)
