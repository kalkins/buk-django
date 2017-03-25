from django.views.generic import DetailView, ListView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.db.models import Q

from .models import Member, MembershipPeriod, LeavePeriod
from .forms import *


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
            context['leave_period_formset'] = LeavePeriodFormset(self.request.POST, instance=self.object)
        else:
            context['membership_period_formset'] = MembershipPeriodFormset(instance=self.object)
            context['leave_period_formset'] = LeavePeriodFormset(instance=self.object)
        return context

    def form_valid(self, form):
        response = super(ChangeMember, self).form_valid(form)
        context = self.get_context_data()
        membership_formset = context['membership_period_formset']
        leave_formset = context['leave_period_formset']
        if membership_formset.is_valid() and leave_formset.is_valid():
            membership_formset.save()
            leave_formset.save()
            return response
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AddMember(PermissionRequiredMixin, CreateView):
    model = Member
    form_class = MemberAddForm
    permission_required = 'members.change_member'
    template_name = 'members/member_add.html'


class MemberStatistics(PermissionRequiredMixin, TemplateView):
    permission_required = 'members.statistics'
    template_name = 'members/member_statistics.html'
    form_class = MemberStatisticsForm

    def get(self, request):
        context = self.get_context_data()

        if 'start' in request.GET:
            form = MemberStatisticsForm(request.GET)
            if form.is_valid():
                context['tables'] = self.get_tables(form)
        else:
            form = MemberStatisticsForm()

        context['form'] = form

        return self.render_to_response(context)


    def get_tables(self, form):
        tables = []
        start = form.cleaned_data['start']
        end = form.cleaned_data['end']

        if form.cleaned_data['members_start']:
            table = {
                'name': form.fields['members_start'].label,
                'cols': ['Navn', 'Startet', 'Sluttet'],
                'rows': [],
                'num': 0,
            }

            for period in MembershipPeriod.objects.filter(Q(end=None) | Q(end__gt=start), start__lt=start):
                table['rows'].append([period.member.get_full_name(), period.start, period.end])
                table['num'] += 1
            tables.append(table)

        if form.cleaned_data['new']:
            table = {
                'name': form.fields['new'].label,
                'cols': ['Navn', 'Startet'],
                'rows': [],
                'num': 0,
            }

            for period in MembershipPeriod.objects.filter(start__range=(start, end), end=None):
                table['rows'].append([period.member.get_full_name(), period.start])
                table['num'] += 1
            tables.append(table)

        if form.cleaned_data['quit']:
            table = {
                'name': form.fields['quit'].label,
                'cols': ['Navn', 'Startet', 'Sluttet'],
                'rows': [],
                'num': 0,
            }

            for period in MembershipPeriod.objects.filter(end__range=(start, end)):
                table['rows'].append([period.member.get_full_name(), period.start, period.end])
                table['num'] += 1
            tables.append(table)

        if form.cleaned_data['joined_quit']:
            table = {
                'name': form.fields['joined_quit'].label,
                'cols': ['Navn', 'Startet', 'Sluttet'],
                'rows': [],
                'num': 0,
            }

            for period in MembershipPeriod.objects.filter(start__range=(start, end), end__range=(start, end)):
                table['rows'].append([period.member.get_full_name(), period.start, period.end])
                table['num'] += 1
            tables.append(table)

        if form.cleaned_data['leave_start']:
            table = {
                'name': form.fields['leave_start'].label,
                'cols': ['Navn', 'Gikk i permisjon', 'Gikk ut av permisjon'],
                'rows': [],
                'num': 0,
            }

            for period in LeavePeriod.objects.filter(start__lt=start, end__range=(start, end)):
                table['rows'].append([period.member.get_full_name(), period.start, period.end])
                table['num'] += 1
            tables.append(table)

        if form.cleaned_data['leave_end']:
            table = {
                'name': form.fields['leave_end'].label,
                'cols': ['Navn', 'Gikk i permisjon', 'Gikk ut av permisjon'],
                'rows': [],
                'num': 0,
            }

            for period in LeavePeriod.objects\
                    .filter(start__range=(start, end))\
                    .filter(Q(end__gt=end) | Q(end=None)):
                table['rows'].append([period.member.get_full_name(), period.start, period.end])
                table['num'] += 1
            tables.append(table)

        if form.cleaned_data['leave_whole']:
            table = {
                'name': form.fields['leave_whole'].label,
                'cols': ['Navn', 'Gikk i permisjon', 'Gikk ut av permisjon'],
                'rows': [],
                'num': 0,
            }

            for period in LeavePeriod.objects.filter(start__lt=start, end__gt=end):
                table['rows'].append([period.member.get_full_name(), period.start, period.end])
                table['num'] += 1
            tables.append(table)

        if form.cleaned_data['leave_part']:
            table = {
                'name': form.fields['leave_part'].label,
                'cols': ['Navn', 'Gikk i permisjon', 'Gikk ut av permisjon'],
                'rows': [],
                'num': 0,
            }

            for period in LeavePeriod.objects.filter(start__gte=start, end__lt=end):
                table['rows'].append([period.member.get_full_name(), period.start, period.end])
                table['num'] += 1
            tables.append(table)

        return tables
