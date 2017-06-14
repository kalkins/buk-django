from django.forms import ModelForm, inlineformset_factory

from .models import Poll, PollOption


class PollForm(ModelForm):
    class Meta:
        model = Poll
        fields = ('title', 'deadline')


PollOptionFormset = inlineformset_factory(
    Poll,
    PollOption,
    fields=('title',),
)
