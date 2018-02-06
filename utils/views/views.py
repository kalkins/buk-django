import re
from django.core.exceptions import ImproperlyConfigured
from django.forms import Form, ModelForm, BaseModelFormSet, modelform_factory
from django.http import HttpResponseRedirect
from django.views.generic.base import View, ContextMixin, TemplateResponseMixin
from django.utils.encoding import force_text
from django.db.models import Model


class MultiFormView(ContextMixin, TemplateResponseMixin, View):
    forms = []
    batch = False
    success_url = None
    http_method_names = ['get', 'post', 'put']

    def __init__(self, *args, **kwargs):
        self.form_names = []
        self.form_instances = {}
        self.form_classes = {}
        self.initial = {}
        self.prefix = {}

        forms = self.get_forms()

        for val in forms:
            if 'factory' in val:
                if not isinstance(val['factory'], dict):
                    raise ImproperlyConfigured('`factory` must be a dictionary.')
                form = modelform_factory(**val['factory'])
            elif 'form' in val:
                if not issubclass(val['form'], (Form, ModelForm, BaseModelFormSet)):
                    raise ImproperlyConfigured('`form` must be a form or formset.')
                form = val['form']
            elif 'model' in val:
                if not issubclass(val['model'], Model):
                    raise ImproperlyConfigured('`model` must be a model.')
                form = modelform_factory(val['model'], fields='__all__')
            else:
                raise ImproperlyConfigured('You must set `form`, `model` or `factory`')

            if 'name' in val:
                name = val['name']
            else:
                try:
                    name = form.prefix
                except AttributeError:
                    # Get the name of the form class, insert underscore between words
                    # and convert it to lower case
                    name = '_'.join(re.findall('[A-Å][^A-Å]*', form.__name__)).lower()

            if name not in self.form_names:
                self.form_names.append(name)
            self.form_classes[name] = form
            self.initial[name] = val['initial'] if 'initial' in val else {}
            self.prefix[name] = val['prefix'] if 'prefix' in val else name

        super().__init__(*args, **kwargs)

    def get_forms(self):
        forms = []
        for cls in self.__class__.__mro__:
            try:
                if cls is not self.__class__:
                    forms += cls.forms
            except AttributeError:
                pass

        return forms + self.forms

    def get_instance(self, name):
        """A wrapper for `get_<name>_instance()`. Return None if that method doesn't exist."""
        try:
            return getattr(self, f'get_{name}_instance')()
        except AttributeError:
            return None

    def include_form(self, name):
        """
        Return whether to include the form with the given name.

        If a method with the name `include_{name}()` exists its
        value is returned. If not True is returned.
        """
        try:
            return getattr(self, f'include_{name}')()
        except AttributeError:
            return True

    def get_initial(self, name):
        """
        Retrieve initial data for the form.

        This is retrieved either from `get_<name>_initial()`, or self.initial[name] if that
        doesn't exist. If no initial data is found, return None.
        """
        try:
            return getattr(self, f'get_{name}_initial')()
        except AttributeError:
            return self.initial[name]

    def get_prefix(self, name):
        """
        Return the prefix to use for the form with the given name.

        If no prefix is set here or in the form class the name is used.
        """
        return self.prefix[name]

    def get_form_kwargs(self, name):
        """
        Return the nameword arguments for instantiating the form with the given name.
        """
        cls = self.get_form_class(name)

        try:
            custom_kwargs = getattr(self, f'get_{name}_kwargs')()
        except AttributeError:
            custom_kwargs = {}

        return {
            # For all forms
            'prefix': self.get_prefix(name),
            'initial': self.get_initial(name),

            'data': self.request.POST if self.request.method in ('POST', 'PUT') else None,
            'files': self.request.PUT if self.request.method == 'PUT' else None,

            **({
                # If the form is a ModelForm
                'instance': self.get_instance(name),
            } if issubclass(cls, ModelForm) else {
                # If the form isn't a ModelForm
            }),

            **custom_kwargs
        }

    def get_success_url(self):
        """
        Returns the supplied success URL, or None if it isn't supplied.
        """
        if self.success_url:
            # Forcing possible reverse_lazy evaluation
            return force_text(self.success_url)

        # Redirect to the current page
        return self.request.path

    def get_form_class(self, name):
        """Return the form class for the given name."""
        return self.form_classes[name]

    def get_form(self, name, form_class=None):
        """Return an instance of the form for the given name."""
        if not form_class:
            form_class = self.get_form_class(name)

        return form_class(**self.get_form_kwargs(name))

    def save_form(self, name, form):
        """Save the form with the given name using `save_<form>()`, or form.save()."""
        try:
            return getattr(self, f'save_{name}')(form)
        except AttributeError:
            form.save()

    def forms_valid(self, forms):
        """
        If the form is valid, redirect to the supplied URL.
        """
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        for name in self.form_names:
            if self.include_form(name):
                form = self.get_form(name)
                self.form_instances[name] = form

        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, *args, **kwargs):
        valid_forms = []

        for name in self.form_names:
            if self.include_form(name):
                form = self.get_form(name)
                self.form_instances[name] = form
                if form.is_valid():
                    valid_forms.append((name, form))

        # If at least one form was valid and batch=False,
        # or all forms are valid and batch=True,
        # we redict (if we are given a success url)
        if valid_forms and (len(valid_forms) == len(self.form_instances) or not self.batch):
            for name, form in valid_forms:
                if isinstance(form, (ModelForm, BaseModelFormSet)):
                    self.save_form(name, form)
                else:
                    try:
                        getattr(self, f'process_{name}')(form)
                    except AttributeError:
                        raise ImproperlyConfigured(
                            f"No method to process '{name}'. Provide the 'process_{name}' method")

            return self.forms_valid(valid_forms)

        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return {**context, **self.form_instances}
