from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from members.models import (Committee, BoardPosition)

from base.models import EditableContent

class Practical(LoginRequiredMixin, TemplateView):
    """
    Display a page with practical information about the marching band,
    and a list of the board and committees and their members.

    The practical information can be edited inline using TinyMCE.

    **Context**

    ``content``
        The practical information.

    ``board_positions``
        A list of board members.

    ``committees``
        A list of committees.

    **Template**

    :template:`practical/practical.html`
    """
    template_name = 'practical/practical.html'

    def get_context_data(self, **kwargs):
        context = super(Practical, self).get_context_data(**kwargs)
        context['content'] = EditableContent.objects.get_or_create(name='practical')[0].text

        context['board_positions'] = BoardPosition.objects.all()
        context['committees'] = Committee.objects.all()

        return context
