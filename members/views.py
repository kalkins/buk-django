import csv

from django.db.models import Q
from django.forms import modelform_factory
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.views.generic import (DetailView, ListView, CreateView,
                                  UpdateView, TemplateView, RedirectView)
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin,
                                        UserPassesTestMixin)

from base.models import EditableContent
from base.widget import FancyCheckbox

from .models import (Member, MembershipPeriod, LeavePeriod,
                     Committee, BoardPosition, PercussionGroup)
from .forms import (MemberAddForm, MemberStatisticsForm,
                    MembershipPeriodFormset, LeavePeriodFormset)


class MemberDetail(DetailView):
    """
    Display an individual :model:`members.Member`.

    **Context**

    ``member``
        An instance of :model:`members.Member`.

    **Template**

    :template:`members/member_detail.html`
    """
    model = Member
    context_object_name = 'member'


class MemberList(LoginRequiredMixin, ListView):
    """
    Display a list of :model:`members.Member`.

    The list is sorted by :model:`members.InstrumentGroup`, group leader,
    first name and last name.

    **Arguments**

    ``show_all``
        Whether to show all members, or just the currently active.

    **Context**

    ``members``
        The list of :model:`members.Member`.

    **Template**

    :template:`members/member_list.html`
    """
    context_object_name = 'members'

    def get_queryset(self):
        if self.kwargs['show_all']:
            return Member.objects.all().prefetch_related(
                    'instrument', 'board_position', 'group_leader_for')
        else:
            return Member.objects.filter(is_active=True).prefetch_related(
                    'instrument', 'board_position', 'group_leader_for')

    def get_context_data(self, **kwargs):
        context = super(MemberList, self).get_context_data(**kwargs)
        context['show_all'] = self.kwargs['show_all']
        return context


class ChangeMember(UserPassesTestMixin, UpdateView):
    """
    Display a form to edit a :model:`members.Member`.

    An user can access this form if it's editing its own
    profile, or if it has the 'members.change_member' permission.

    **Context**

    ``form``
        The form for editing the :model:`members.Member`.

    ``membership_period_formset``
        An inline formset for adding/editing :model:`members.MembershipPeriod`
        related to the :model:`members.Member`.

    ``leave_period_formset``
        An inline formset for adding/editing :model:`members.LeavePeriod`
        related to the :model:`members.Member`.

    **Template**

    :template:`members/member_change.html`
    """
    model = Member
    template_name = 'members/member_change.html'

    def test_func(self, *args, **kwargs):
        user = self.request.user
        return user.has_perm('members.change_member') or user == self.get_object()

    def get_form_class(self, *args, **kwargs):
        fields = ['email', 'first_name', 'last_name', 'instrument', 'phone',
                  'birthday', 'address', 'zip_code', 'city', 'origin', 'occupation',
                  'has_car', 'has_towbar', 'musical_background', 'about_me']

        widgets={"has_car": FancyCheckbox, "has_towbar": FancyCheckbox}
        if self.request.user.has_perm('members.change_percussion_group'):
            fields.insert(4, 'percussion_group')

        return modelform_factory(Member, fields=fields, widgets=widgets)

    def get_context_data(self, **kwargs):
        context = super(ChangeMember, self).get_context_data(**kwargs)
        if self.request.POST:
            context['membership_period_formset'] = MembershipPeriodFormset(
                    self.request.POST, instance=self.object)
            context['leave_period_formset'] = LeavePeriodFormset(
                    self.request.POST, instance=self.object)
        else:
            context['membership_period_formset'] = MembershipPeriodFormset(instance=self.object)
            context['leave_period_formset'] = LeavePeriodFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        membership_formset = context['membership_period_formset']
        leave_formset = context['leave_period_formset']
        if form.is_valid() and membership_formset.is_valid() and leave_formset.is_valid():
            membership_formset.save()
            leave_formset.save()
            return super(ChangeMember, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AddMember(PermissionRequiredMixin, CreateView):
    """
    Display a form for editing a :model:`members.Member`.

    **Context**

    ``form``
        The form for editing the :model:`members.Member`.

    **Template**

    :template:`members/member_add.html`
    """
    model = Member
    form_class = MemberAddForm
    permission_required = 'members.change_member'
    template_name = 'members/member_add.html'


class MemberStatistics(PermissionRequiredMixin, TemplateView):
    """
    Display statistics about :model:`members.Member`, and a form
    for changing what statistics are displayed.

    **Context**

    ``form``
        The form for adding the :model:`members.Member`.

    **Template**

    :template:`members/member_add.html`
    """
    permission_required = 'members.statistics'
    template_name = 'members/member_statistics.html'
    form_class = MemberStatisticsForm

    def get(self, request):
        context = self.get_context_data()

        if 'start' in request.GET:
            form = MemberStatisticsForm(request.GET)
            if form.is_valid():
                context['tables'] = self.get_tables(form)

                if 'csv' in request.GET:
                    start = form.cleaned_data['start']
                    end = form.cleaned_data['end']
                    filename = 'statistikk-%s--%s' % (start, end)

                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

                    writer = csv.writer(response)
                    writer.writerow(['Medlemsstatistikk for perioden %s til %s' % (start, end)])
                    writer.writerow([])
                    writer.writerow([])

                    for table in context['tables']:
                        writer.writerow([table['name']])
                        if table['num']:
                            writer.writerow(table['cols'])
                            for row in table['rows']:
                                writer.writerow(row)
                            writer.writerow(['Totalt:', table['num']])
                        else:
                            writer.writerow(['Ingen'])
                        writer.writerow([])
                        writer.writerow([])

                    return response
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

            for period in MembershipPeriod.objects.filter(
                    Q(end=None) | Q(end__gt=start), start__lt=start)\
                    .prefetch_related('member'):
                table['rows'].append([period.member.get_full_name(), period.start, period.end])
                table['num'] += 1
            tables.append(table)

        if form.cleaned_data['members_end']:
            table = {
                'name': form.fields['members_end'].label,
                'cols': ['Navn', 'Startet', 'Sluttet'],
                'rows': [],
                'num': 0,
            }

            for period in MembershipPeriod.objects.filter(
                    Q(end=None) | Q(end__gt=end), start__lt=end)\
                    .prefetch_related('member'):
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

            for period in MembershipPeriod.objects.filter(start__range=(start, end), end=None)\
                    .prefetch_related('member'):
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

            for period in MembershipPeriod.objects.filter(end__range=(start, end))\
                    .prefetch_related('member'):
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

            for period in MembershipPeriod.objects.filter(
                    start__range=(start, end), end__range=(start, end))\
                    .prefetch_related('member'):
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

            for period in LeavePeriod.objects.filter(start__lt=start, end__range=(start, end))\
                    .prefetch_related('member'):
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
                    .filter(Q(end__gt=end) | Q(end=None))\
                    .prefetch_related('member'):
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

            for period in LeavePeriod.objects.filter(
                    start__lt=start, end__gt=end).prefetch_related('member'):
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

            for period in LeavePeriod.objects.filter(
                    start__gte=start, end__lt=end).prefetch_related('member'):
                table['rows'].append([period.member.get_full_name(), period.start, period.end])
                table['num'] += 1
            tables.append(table)

        return tables


class PercussionGroupList(LoginRequiredMixin, ListView):
    """
    Display a list of all percussion groups, including members,
    and the members who don't have a group.

    **Context**
    ``groups``
        A list of the percussion groups.

    ``unassigned``
        A list of the members who are not assigned to a
        percussion group.

    **Template**

    :model:`percussion_groups/list.html`
    """
    context_object_name = 'groups'
    template_name = 'percussion_groups/list.html'

    def get_queryset(self):
        return PercussionGroup.objects.all().prefetch_related('members')

    def get_context_data(self, **kwargs):
        context = super(PercussionGroupList, self).get_context_data(**kwargs)
        context['unassigned'] = Member.objects\
                                      .filter(is_active=True, percussion_group=None)\
                                      .order_by('is_on_leave', 'first_name', 'last_name')
        return context


class AddPercussionGroup(PermissionRequiredMixin, RedirectView):
    """Add a percussion group, then redirect to the list of groups."""
    permission_required = 'members.change_percussion_group'
    pattern_name = 'percussion_group_list'

    def get(self, *args, **kwargs):
        group = PercussionGroup()
        group.save()

        return super(AddPercussionGroup, self).get(*args, **kwargs)


class DeletePercussionGroup(PermissionRequiredMixin, RedirectView):
    """Remove a percussion group, then redirect to the list of groups."""
    permission_required = 'members.change_percussion_group'
    url = reverse_lazy('percussion_group_list')

    def get(self, *args, **kwargs):
        group = get_object_or_404(PercussionGroup, pk=kwargs['pk'])
        group.delete()

        return super(DeletePercussionGroup, self).get(*args, **kwargs)


class ChangePercussionGroup(PermissionRequiredMixin, TemplateView):
    """
    Display a form for editing a percussion group.

    The form list all members and allows for picking out individual
    members of the current group, and its leader.

    The form must rely on AJAX to submit the data.

    **Context**
    ``group``
        The group currently being edited.

    ``other_groups``
        A list of the other percussion groups.

    ``unassigned``
        A list of the members who are not assigned to a
        percussion group.

    **Template**

    :model:`percussion_groups/change.html`
    """
    permission_required = 'members.change_percussion_group'
    template_name = 'percussion_groups/change.html'
    http_method_names = ['get', 'post']

    def post(self, request, pk):
        if 'leader' not in request.POST or 'members[]' not in request.POST:
            raise Http404

        leader = request.POST['leader']
        group = get_object_or_404(PercussionGroup, pk=pk)
        group.leader_id = leader
        group.save()

        members = request.POST.getlist('members[]')
        members.append(leader)

        # Remove old members, and add new ones
        Member.objects.filter(percussion_group=group).update(percussion_group=None)
        Member.objects.filter(pk__in=members).update(percussion_group=group)

        # If a member is the leader for another group, remove the leadership
        PercussionGroup.objects\
                       .exclude(pk=group.pk)\
                       .filter(leader__percussion_group=group)\
                       .update(leader=None)

        return JsonResponse({
            'success': True,
            'next': reverse('percussion_group_change', kwargs={'pk': pk}),
        })

    def get_context_data(self, **kwargs):
        context = super(ChangePercussionGroup, self).get_context_data(**kwargs)
        context['group'] = get_object_or_404(PercussionGroup, pk=kwargs['pk'])
        context['other_groups'] = PercussionGroup.objects\
                                                 .exclude(pk=kwargs['pk'])\
                                                 .prefetch_related('members')
        context['unassigned'] = Member.objects\
                                      .filter(is_active=True, percussion_group=None,
                                              percussion_group_leader_for=None)\
                                      .order_by('is_on_leave', 'first_name', 'last_name')

        return context
