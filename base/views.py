from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse
from django import views

from .models import EditableContent

class EditableContentSave(PermissionRequiredMixin, views.View):
    permission_required = 'base.edit_content'

    def post(self, request):
        if 'name' in request.POST and 'content' in request.POST:
            try:
                obj = EditableContent.objects.get(name=request.POST['name'])
                obj.text = request.POST['content']
                obj.save()

                return JsonResponse({'success': True})
            except ObjectDoesNotExist:
                pass

        return JsonResponse({'success': False})
