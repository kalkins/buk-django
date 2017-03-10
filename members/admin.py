from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import Member, Instrument, BoardPosition, Committee


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        # This attribute is required for the form to work, but it will
        # be overwritten by the UserAdmin
        fields = ('email',)


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
        (None, {'fields':
            ('first_name', 'last_name', 'instrument', 'email',
            'joined_date', 'quit_date', 'is_active')}
        ),
        ('Praktisk informasjon', {'fields': ('has_car', 'has_towbar')}),
        ('Personlig informasjon', {'fields': (
            'birthday', 'phone', 'address', 'zip_code', 'city', 'origin', 'occupation',
            'musical_background', 'about_me')
        }),
    )

    # Fieldsets for the add-user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'instrument', 'birthday', 'phone', 'joined_date',
                'address', 'zip_code', 'city')
        }),
    )


class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_leader')
    search_fields = ('name', 'group_leader')
    ordering = ('order', 'name')

    fieldsets = (
        (None, {'fields': ('name', 'group_leader')}),
    )

    add_fieldsets = (
        (None, {'fields': ('name',)}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(InstrumentAdmin, self).get_form(request, obj, **kwargs)
        if obj and form.base_fields['group_leader']:
            # Only someone playing the instrument can be group leader
            form.base_fields['group_leader'].queryset = Member.objects.filter(instrument=obj)
        else:
            # If it's a new instrument disable the group leader select
            form.base_fields['group_leader'].disabled = True
            form.base_fields['group_leader'].help_text = (
                'Du må legge til medlemmer i instrumentgruppen før du kan velge en gruppeleder'
            )
        return form


class BoardPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'holder', 'email')
    ordering = ('order', 'title')


class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'member_count')
    ordering = ('order', 'name')
    filter_horizontal = ('members',)

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Antall medlemmer'

admin.site.register(Member, UserAdmin)
admin.site.register(Instrument, InstrumentAdmin)
admin.site.register(BoardPosition, BoardPositionAdmin)
admin.site.register(Committee, CommitteeAdmin)
