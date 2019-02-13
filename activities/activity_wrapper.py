from django.forms import modelform_factory

from .models import Activity, Rehearsal, Concert, Other


ACTIVITY_TYPES = {
    Rehearsal: {},
    Concert: {'fields': ['price', 'price_student']},
    Other: {},
}


class ActivityWrapper:
    def __init__(self, instance):
        self.instance = Activity.objects.get_subclass(pk=instance.pk)
        self.model = self.instance.__class__
        self.name = self.get_name(self.model)
        self.form = self.get_form(self.model)

        entry = ACTIVITY_TYPES[self.model]

        template = entry['template'] if 'template' in entry else None
        self.detail_template = entry.get('detail_template', template)
        self.form_template = entry.get('form_template', template)

    @classmethod
    def get(cls, model, key, default=None):
        return ACTIVITY_TYPES[model].get(key, default)

    @classmethod
    def get_form(cls, model):
        form = cls.get(model, 'form')
        if form is None:
            fields = cls.get(model, 'fields')
            if fields is None:
                form = modelform_factory(model, fields=[])
            else:
                form = modelform_factory(model, fields=fields)

        return form

    @classmethod
    def all_forms(cls):
        """Return a list of tuples of the name and form class of each activity model"""
        return [
            (cls.get_name(model), cls.get_form(model))
            for model in ACTIVITY_TYPES
            if cls.get_form(model)
        ]

    @classmethod
    def get_name(cls, model):
        return cls.get(model, 'name', model._meta.verbose_name)

    @classmethod
    def all_names(cls):
        return [cls.get_name(model) for model in ACTIVITY_TYPES]

    @classmethod
    def get_model(cls, name):
        for model in ACTIVITY_TYPES:
            if cls.get_name(model) == name:
                return model
