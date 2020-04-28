from django.db import models

from base import form_fields


class CustomManyToManyField(models.ManyToManyField):
    def formfield(self, *args, **kwargs):
        defaults = {
            'field_name': self.verbose_name,
            'form_class': form_fields.CustomModelMultipleChoiceField,
        }
        defaults.update(kwargs)
        return super().formfield(*args, **defaults)


class CustomDateField(models.DateField):
    def formfield(self, *args, **kwargs):
        defaults = {'form_class': form_fields.CustomDateField}
        defaults.update(kwargs)
        return super().formfield(*args, **defaults)


class CustomTimeField(models.TimeField):
    def formfield(self, *args, **kwargs):
        defaults = {'form_class': form_fields.CustomTimeField}
        defaults.update(kwargs)
        return super().formfield(*args, **defaults)


class CustomDateTimeField(models.DateTimeField):
    def formfield(self, *args, **kwargs):
        defaults = {'form_class': form_fields.CustomDateTimeField}
        defaults.update(kwargs)
        return super().formfield(*args, **defaults)
