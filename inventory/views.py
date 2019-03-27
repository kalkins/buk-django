from django.shortcuts import render
from django.views.generic import TemplateView
from inventory.models import Instrument, Hat, Jacket, Pants


class InventoryList(TemplateView):
    """
    Displays a list of all inventory item with links for adding and removing items

    **Template**

    :template:`inventory/inventory_list.html`
    """

    template_name = 'inventory/inventory_list.html'

    def get_context_data(self, **kwargs):
        context = super(InventoryList, self).get_context_data(**kwargs)
        context['instruments'] = Instrument.objects.all()
        context['hats'] = Hat.objects.all()
        context['jackets'] = Jacket.objects.all()
        context['pants'] = Pants.objects.all()
        return context
