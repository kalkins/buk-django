from django.contrib import admin

from inventory.models import Jacket, Hat, Pants, Instrument

admin.site.register(Jacket)
admin.site.register(Hat)
admin.site.register(Pants)
admin.site.register(Instrument)
