from django import forms

from .widgets import ManyToManyWidget, DatePickerWidget, TimePickerWidget, DateTimePickerWidget


class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, field_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.widget = ManyToManyWidget(
            field_name,
            False,
        )


class CustomDateField(forms.DateField):
    widget = DatePickerWidget


class CustomTimeField(forms.TimeField):
    widget = TimePickerWidget


class CustomDateTimeField(forms.DateTimeField):
    widget = DateTimePickerWidget
