from django.http import HttpResponseRedirect, Http404
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, CreateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy

from .models import Activity, Rehearsal, ActivityPeriod
from .activity_wrapper import ActivityWrapper
from .forms import ActivityForm, ActivityPeriodFormset


class ActivityMixin(SingleObjectMixin):
    model = Activity
    context_object_name = 'activity'

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)

        try:
            return queryset.get_subclass(pk=pk)
        except queryset.model.DoesNotExist:
            return super().get_object(queryset)


class ActivityFormMixin(ActivityMixin, TemplateResponseMixin, ModelFormMixin):
    form_class = ActivityForm

    def get_current_type(self, form=None):
        """Return a tuple of the name and class of the current activity model"""
        if self.object:
            activity_wrapper = ActivityWrapper(self.object)
            name = activity_wrapper.name
            form = activity_wrapper.form
        elif form and self.request.method == 'POST':
            name = form.cleaned_data['activity_type']
            for n, f in ActivityWrapper.all_forms():
                if n == name:
                    form = f
                    break
            else:
                raise Http404(f'Invalid activity type {name}')
        else:
            default_type = Rehearsal

            name = ActivityWrapper.get_name(default_type)
            form = ActivityWrapper.get_form(default_type)

        return (name, form)

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)

        form_kwargs = self.get_form_kwargs()

        data['activity_period_formset'] = ActivityPeriodFormset(**form_kwargs)

        data['current_type'] = self.get_current_type()[0]

        data['activity_forms'] = [
            [name, form_class(**form_kwargs)]
            for name, form_class in ActivityWrapper.all_forms()
        ]

        return data

    def form_valid(self, form):
        # The base Activity form is valid, but we have to check that
        # the specific subclass form also is valid
        name, sub_form_class = self.get_current_type(form)
        model = ActivityWrapper.get_model(name)

        if self.object and self.object.pk:
            instance = self.object
        else:
            instance = model()

        kwargs = self.get_form_kwargs()
        kwargs['instance'] = instance

        form = self.get_form_class()(**kwargs)
        # Note: This doesn't save many-to-many fields
        instance = form.save(commit=False)

        sub_form = sub_form_class(**kwargs)

        if not sub_form.is_valid():
            return self.form_invalid(form)

        self.object = sub_form.save()
        # Now that the instance is saved to the database
        # we can save the many-to-many fields
        form.save_m2m()

        kwargs['instance'] = self.object
        activity_formset = ActivityPeriodFormset(**kwargs)
        if not activity_formset.is_valid():
            return self.form_invalid(form)

        activity_formset.save()

        # The forms have been saved, so we can redirect the user.
        # Note that we can't call super().form_valid(),
        # as that would save the object again
        return HttpResponseRedirect(self.get_success_url())

    def get_template_names(self):
        return super().get_template_names() + [
            f'activities/activity_form.html',
        ]


class CreateActivity(ActivityFormMixin, CreateView):
    template_name_suffix = '_create'


class UpdateActivity(ActivityFormMixin, UpdateView):
    template_name_suffix = '_update'


class DeleteActivity(DeleteView):
    model = Activity
    success_url = reverse_lazy('activity_list')


class ActivityDetailView(ActivityMixin, DetailView):
    template_name = 'activities/activity_detail.html'

    def get_template_names(self):
        activity_wrapper = ActivityWrapper(self.object)
        class_name = activity_wrapper.model.__name__.lower()

        # This defines the order to look for template files
        template_names = []

        # Prefer the template spesified on the model, if available
        if activity_wrapper.detail_template is not None:
            template_names.append(activity_wrapper.detail_template)

        # If not, use a generic name for each type
        template_names += [
            f'activities/{class_name}_detail.html',
            f'activities/{class_name}.html',
        ]

        # If no other templates are available, use the default one
        template_names += super().get_template_names()

        return template_names


class ActivityListView(ListView):
    model = ActivityPeriod
    template_name = 'activities/activity_list.html'
    context_object_name = 'periods'

    def get_queryset(self):
        return ActivityPeriod.objects.future_inclusive()
