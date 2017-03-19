from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django import forms

from .models import *
from base.forms import BasePeriodFormset

class MemberAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'E-post'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Passord'}))


class MemberPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'E-post'}))


class MemberAddForm(forms.ModelForm):
    joined_date = forms.DateField(label='Startet i BUK:', required=True)

    class Meta:
        model = Member
        fields = ['email', 'first_name', 'last_name', 'instrument', 'phone', 'joined_date', 'birthday',
                'address', 'zip_code', 'city']

    def save(self, *args, **kwargs):
        obj = super(MemberAddForm, self).save(*args, **kwargs)
        MembershipPeriod.objects.create(member=obj, start=self.cleaned_data['joined_date'])
        return obj


MembershipPeriodFormset = forms.inlineformset_factory(
    Member,
    MembershipPeriod,
    formset = BasePeriodFormset,
    extra = 1,
    fields = ('start', 'end'),
)
