from django.forms import CheckboxInput
from django.contrib.admin.widgets import FilteredSelectMultiple


class FancyCheckbox(CheckboxInput):
    template_name="widgets/fancycheckbox.html"


class ManyToManyWidget(FilteredSelectMultiple):
    class Media:
        css = {
            'widgets/manytomany.css',
        }
