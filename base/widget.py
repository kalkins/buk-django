from django.forms import CheckboxInput

class FancyCheckbox(CheckboxInput):
    template_name="widgets/fancycheckbox.html"
