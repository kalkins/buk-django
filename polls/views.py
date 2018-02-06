from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from utils.views import MultiFormView
from .models import Poll
from .forms import PollForm, PollOptionFormset, PollAnswerForm


class PollCreateFormView(MultiFormView):
    forms = [
        {'name': 'poll_form', 'form': PollForm},
        {'name': 'poll_option_formset', 'form': PollOptionFormset},
    ]

    def include_poll(self):
        return self.request.method == 'GET' or 'poll-form-toggle' in self.request.POST

    def include_poll_form(self):
        return self.include_poll()

    def include_poll_option_formset(self):
        return self.include_poll()

    def save_poll_option_formset(self, formset):
        options = formset.save(commit=False)
        for option in options:
            option.poll = self.form_instances['poll_form'].instance
            option.save()


class PollAnswerFormView(SingleObjectMixin, MultiFormView):
    forms = [
        {'name': 'poll_answer_form', 'form': PollAnswerForm},
    ]

    def include_poll_answer_form(self):
        return bool(self.get_object().poll)

    def get_poll_answer_form_kwargs(self):
        return {
            'member': self.request.user,
            'poll': self.get_object().poll,
        }

    def process_poll_answer_form(self, form):
        form.save(self.request.user)


class PollStatistics(LoginRequiredMixin, DetailView):
    """
    Display information about what people chose
    in a given poll.
    """
    model = Poll
    context_object_name = 'poll'
    template_name = 'polls/poll_statistics.html'
