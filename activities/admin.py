from django.contrib import admin

from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'visibility', 'percussion_group')
    filter_horizontal = ('bakers',)
