from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django import forms

from base.forms import BasePeriodFormset

from .models import Member, MembershipPeriod, LeavePeriod, Committee, CommitteeMembership


class MemberAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'E-post'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Passord'}))


class MemberPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'E-post'}))


class MemberAddForm(forms.ModelForm):
    joined_date = forms.DateField(label='Startet i BUK:', required=True)

    class Meta:
        model = Member
        fields = ['email', 'first_name', 'last_name', 'instrument', 'phone',
                  'joined_date', 'birthday', 'address', 'zip_code', 'city']

    def save(self, *args, **kwargs):
        obj = super(MemberAddForm, self).save(*args, **kwargs)
        MembershipPeriod.objects.create(member=obj, start=self.cleaned_data['joined_date'])
        return obj


MembershipPeriodFormset = forms.inlineformset_factory(
    Member,
    MembershipPeriod,
    formset=BasePeriodFormset,
    extra=1,
    fields=('start', 'end'),
)


LeavePeriodFormset = forms.inlineformset_factory(
    Member,
    LeavePeriod,
    formset=BasePeriodFormset,
    extra=1,
    fields=('start', 'end'),
)


class MemberStatisticsForm(forms.Form):
    start = forms.DateField(label='Start', required=True)
    end = forms.DateField(label='Slutt', required=True)

    members_start = forms.BooleanField(
            label='Medlemsliste ved starten av perioden', label_suffix='',
            required=False, initial=True)
    members_end = forms.BooleanField(
            label='Medlemsliste ved utgangen av perioden', label_suffix='',
            required=False, initial=True)
    new = forms.BooleanField(
            label='Medlemmer som begynte denne perioden', label_suffix='',
            required=False, initial=True,
            help_text='Inkluderer ikke de som sluttet og begynte i løpet av perioden')
    quit = forms.BooleanField(
            label='Medlemmer som sluttet denne perioden', label_suffix='',
            required=False, initial=True,
            help_text='Inkluderer ikke de som sluttet og begynte i løpet av perioden')
    joined_quit = forms.BooleanField(
            label='Medlemmer som begynte og sluttet denne perioden',
            label_suffix='', required=False, initial=True)
    leave_start = forms.BooleanField(
            label='Medlemmer i permisjon ved inngangen til denne perioden', label_suffix='',
            required=False)
    leave_end = forms.BooleanField(
            label='Medlemmer i permisjon ved utgangen av denne perioden',
            label_suffix='', required=False, initial=True)
    leave_whole = forms.BooleanField(
            label='Medlemmer i permisjon i hele perioden', label_suffix='', required=False)
    leave_part = forms.BooleanField(
            label='Medlemmer i permisjon i løpet av perioden', label_suffix='', required=False)


class CommitteeChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the queryset for the leader
        queryset = Member.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['leader'].queryset = queryset

    class Meta:
        model = Committee
        fields = ['name', 'description', 'email', 'order',
                  'leader', 'leader_title']


class CommitteeMembershipForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the queryset for the member
        queryset = Member.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['member'].queryset = queryset

    class Meta:
        model = CommitteeMembership
        fields = ('member', 'title')


CommitteeMembershipFormset = forms.inlineformset_factory(
    Committee,
    CommitteeMembership,
    extra=3,
    form=CommitteeMembershipForm,
)
