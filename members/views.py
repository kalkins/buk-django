from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from .models import Member


class MemberDetail(DetailView):
    model = Member
    context_object_name = 'member'


class MemberList(LoginRequiredMixin, ListView):
    context_object_name = 'members'

    def get_queryset(self):
        if self.kwargs['show_all']:
            return Member.objects.all()
        else:
            return Member.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super(MemberList, self).get_context_data(**kwargs)
        context['show_all'] = self.kwargs['show_all']
        return context
