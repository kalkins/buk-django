from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (Member, Instrument, MembershipPeriod,
                     LeavePeriod, Committee, BoardPosition,
                     PercussionGroup)


class MembershipPeriodInline(admin.TabularInline):
    model = MembershipPeriod
    extra = 1


class LeavePeriodInline(admin.TabularInline):
    model = LeavePeriod
    extra = 1


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        # This attribute is required for the form to work, but it will
        # be overwritten by the UserAdmin
        fields = ('email',)


@admin.register(Member)
class UserAdmin(BaseUserAdmin):
    form = MemberForm
    add_form = MemberForm

    # The fields to be displayed in the list view of the users
    list_display = ('email', 'is_active', 'get_full_name', 'instrument', 'phone',
                    'get_full_address', 'has_car', 'has_towbar')
    list_filter = ('is_active', 'instrument', 'groups')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-is_active', 'instrument', 'first_name', 'last_name')
    filter_horizontal = ('groups',)

    # Fieldsets for the change-user form
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'instrument',
                       'email', 'is_admin', 'is_superuser')
        }),
        ('Praktisk informasjon', {
            'fields': ('percussion_group', 'has_car', 'has_towbar')
        }),
        ('Personlig informasjon', {
            'fields': ('birthday', 'phone', 'address', 'zip_code',
                       'city', 'origin', 'occupation',
                       'musical_background', 'about_me')
        }),
    )

    # Fieldsets for the add-user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'instrument',
                       'birthday', 'phone', 'address', 'zip_code', 'city')
        }),
    )

    inlines = [
        MembershipPeriodInline,
        LeavePeriodInline
    ]


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_leader', 'order')
    search_fields = ('name', 'group_leader')

    fieldsets = (
        (None, {'fields': ('name', 'order', 'group_leader')}),
    )

    add_fieldsets = (
        (None, {'fields': ('name', 'order')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(InstrumentAdmin, self).get_form(request, obj, **kwargs)
        if obj and form.base_fields['group_leader']:
            # Only someone playing the instrument can be group leader
            form.base_fields['group_leader'].queryset = Member.objects\
                    .filter(is_active=True)\
                    .filter(instrument=obj)
        else:
            # If it's a new instrument disable the group leader select
            form.base_fields['group_leader'].disabled = True
            form.base_fields['group_leader'].help_text = (
                'Du må legge til medlemmer i instrumentgruppen før du kan velge en gruppeleder'
            )
        return form


@admin.register(BoardPosition)
class BoardPositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'holder', 'email')
    ordering = ('order', 'name')


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    readonly_fields = ('inherited_permissions',)
    filter_horizontal = ('parents', 'own_permissions')
    list_display = ('name', 'leader', 'member_count')
    ordering = ('order', 'name')

    fieldsets = (
        (None, {
            'fields': ('name',),
        }),
        (None, {
            'description': 'Lederen for komiteen. Bare én av disse kan bli satt',
            'fields': ('leader_board', 'leader_member')
        }),
        ('Rettigheter', {
            'classes': ('collapse',),
            'fields': ('parents', 'own_permissions'),
        }),
        ('Arvede rettigheter', {
            'description': """
                Rettigheter som er arvet fra overgrupper, ikke inkludert de som
                overlapper med rettighetene til denne komiteen.
            """,
            'classes': ('collapse',),
            'fields': ('inherited_permissions',),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj:
            form.base_fields['parents'].queryset = obj.get_available_parents()

        return form

    def inherited_permissions(self, obj):
        return '\n'.join(map(str, obj.inherited_permissions))
    inherited_permissions.short_description = 'Arvede rettigheter'

    def member_count(self, obj):
        return obj.user_set.count()
    member_count.short_description = 'Antall medlemmer'


@admin.register(PercussionGroup)
class PercussionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'member_count')

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Antall medlemmer'
