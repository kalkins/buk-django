from django.views.generic import DetailView
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Poll
from .forms import PollForm, PollOptionFormset


class PollFormMixin(ModelFormMixin):
    poll = None
    poll_form = None
    poll_option_formset = None

    def get_form(self, *args, **kwargs):
        form = super(PollFormMixin, self).get_form(*args, **kwargs)

        if self.form.instance:
            self.poll = self.form.instance.poll

        if 'poll_form_toggle' in self.request.POST:
            self.poll_form = PollForm(request.POST, instance=self.poll)

            if self.poll_form.is_valid():
                self.poll = self.poll_form.instance

                self.poll_option_formset = PollOptionFormset(request.POST)
                if not self.poll_option_formset.is_valid():
                    return self.form_invalid()
            else:
                return self.form_invalid()
        

    def get_context_data(self, *args, **kwargs):
        context = super(PollFormMixin, self).get_context_data(*args, **kwargs)
        context['poll_form'] = PollForm(self.request.POST, instance=self.poll)
        context['poll_option_formset'] = PollOptionFormset(self.request.POST,
                                                           instance=self.poll)

        return context

    def form_valid(self, form):
        if self.poll:
            self.poll.save()
            form.instance.poll = self.poll

            for instance in self.poll_option_formset.save(commit=False):
                instance.poll = self.poll
                instance.save()

        return super(PollFormMixin, self).form_valid(form)


class PollStatistics(LoginRequiredMixin, DetailView):
    """
    Display information about what people chose
    in a given poll.
    """
    model = Poll
    context_object_name = 'poll'
    template_name = 'polls/poll_statistics.html'
