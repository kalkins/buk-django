from django.forms import CheckboxInput, DateInput, DateTimeInput, TimeInput
from django.contrib.admin.widgets import FilteredSelectMultiple


class FancyCheckbox(CheckboxInput):
    template_name = "widgets/fancycheckbox.html"


class FlatpickrMixin:
    classes = []

    def __init__(self, attrs={}):
        classes = set(['flatpickr', *self.classes])

        if 'class' in attrs:
            classes |= set(attrs['class'].split(' '))

        attrs['class'] = ' '.join(classes)
        super().__init__(attrs)

    class Media:
        css = {
            'all': ('base/css/flatpickr.min.css',),
        }
        js = (
            'base/js/flatpickr.min.js',
            'base/js/flatpickr-no.js',
            'widgets/flatpickr.js',
        )


class DatePickerWidget(FlatpickrMixin, DateInput):
    classes = ['date']


class DateTimePickerWidget(FlatpickrMixin, DateTimeInput):
    classes = ['datetime']


class TimePickerWidget(FlatpickrMixin, TimeInput):
    classes = ['time']


class ManyToManyWidget(FilteredSelectMultiple):
    class Media:
        css = {
            'all': ('widgets/manytomany.css',),
        }
