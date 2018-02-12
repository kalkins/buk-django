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
        if 'member' not in kwargs:
            raise ValueError('The constructor must be passed both a member object')
        if 'poll' not in kwargs:
            raise ValueError('The constructor must be passed both a poll object')

        self.member = kwargs.pop('member')
        self.poll = kwargs.pop('poll')
        super(PollAnswerForm, self).__init__(*args, **kwargs)

        self.fields['options'].queryset = self.poll.options

        if self.poll.is_past_deadline:
            self.fields['options'].disabled = True

        for option in self.poll.options.all():
            if self.member in option.members.all():
                self.fields['options'].initial = option
                break
        else:
            self.fields['options'].initial = None

    def clean(self):
        if self.poll.is_past_deadline:
            raise forms.ValidationError('Fristen for påmeldingen har passert')
        return super().clean()

    def save(self):
        if not self.errors:
            for option in self.fields['options'].queryset.all():
                option.members.remove(self.member)

            option = self.cleaned_data['options']
            option.members.add(self.member)
        else:
            raise ValueError('Data doesn\'t validate')
