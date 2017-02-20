from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django import forms

class MemberAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'E-post'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Passord'}))


class MemberPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'E-post'}))
