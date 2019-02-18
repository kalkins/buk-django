from django import forms

from base.forms import BasePeriodFormset
from base.widgets import ManyToManyWidget

from .models import Activity, ActivityPeriod
from .activity_wrapper import ActivityWrapper


def activity_choices():
    return [
        (name, name.capitalize())
        for name in ActivityWrapper.all_names()
    ]


class ActivityForm(forms.ModelForm):
    activity_type = forms.ChoiceField(label='Type', choices=activity_choices)

    class Meta:
        model = Activity
        fields = ['title', 'activity_type', 'visibility', 'description',
                  'description_internal', 'location', 'bakers', 'percussion_group']
        widgets = {
            'bakers': ManyToManyWidget(Activity.bakers.field.verbose_name, False),
        }


ActivityPeriodFormset = forms.inlineformset_factory(
    Activity,
    ActivityPeriod,
    formset=BasePeriodFormset,
    min_num=1,
    extra=2,
    fields=('start', 'end'),
)
