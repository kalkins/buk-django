from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render

from .models import Member, MembershipPeriod
from .forms import MembershipPeriodFormset


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


class ChangeMember(PermissionRequiredMixin, UpdateView):
    model = Member
    permission_required = 'members.change_member'
    template_name = 'members/member_change.html'
    fields = ['email', 'first_name', 'last_name', 'instrument', 'phone', 'birthday',
        'address', 'zip_code', 'city', 'origin', 'occupation', 'has_car', 'has_towbar',
        'musical_background', 'about_me']

    def get_context_data(self, **kwargs):
        context = super(ChangeMember, self).get_context_data(**kwargs)
        if self.request.POST:
            context['membership_period_formset'] = MembershipPeriodFormset(self.request.POST, instance=self.object)
        else:
            context['membership_period_formset'] = MembershipPeriodFormset(instance=self.object)
        return context

    def form_valid(self, form):
        response = super(ChangeMember, self).form_valid(form)
        context = self.get_context_data()
        membership_formset = context['membership_period_formset']
        if membership_formset.is_valid():
            membership_formset.save()
            return response
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AddMember(PermissionRequiredMixin, CreateView):
    model = Member
    permission_required = 'members.change_member'
    template_name = 'members/member_add.html'
    fields = ['email', 'first_name', 'last_name', 'instrument', 'phone', 'birthday',
            'address', 'zip_code', 'city']
