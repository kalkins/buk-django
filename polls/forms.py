from django import forms

from .models import Poll, PollOption


class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ('title', 'deadline')


PollOptionFormset = forms.inlineformset_factory(
    Poll,
    PollOption,
    fields=('title',),
)


class PollAnswerForm(forms.Form):
    options = forms.ModelChoiceField(queryset=None, widget=forms.RadioSelect, empty_label=None)

    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member')
        poll = kwargs.pop('poll')
        super(PollAnswerForm, self).__init__(*args, **kwargs)

        self.fields['options'].queryset = poll.options

        if poll.is_past_deadline:
            self.fields['options'].disabled = True

        for option in poll.options.all():
            if member in option.members.all():
                self.fields['options'].initial = option
                break
        else:
            self.fields['options'].initial = None

    def save(self, member):
        if self.is_valid():
            for option in self.fields['options'].queryset.all():
                option.members.remove(member)

            option = self.cleaned_data['options']
            option.members.add(member)
