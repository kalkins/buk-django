from django.views.generic import DetailView, ListView, CreateView, UpdateView
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


class ChangeMember(UpdateView):
    model = Member
    template_name = 'members/member_change.html'
    fields = ['email', 'first_name', 'last_name', 'instrument', 'phone', 'birthday',
            'address', 'zip_code', 'city', 'origin', 'occupation', 'joined_date',
            'quit_date', 'has_car', 'has_towbar', 'musical_background', 'about_me']
