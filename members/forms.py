from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django import forms

from .models import *

class MemberAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'E-post'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Passord'}))


class MemberPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'E-post'}))


MembershipPeriodFormset = forms.inlineformset_factory(
    Member,
    MembershipPeriod,
    extra = 1,
    can_delete = False,
    fields = ('start', 'end'),
)
