import os

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse
from django import views

from .models import EditableContent, EditableContentImage

class EditableContentSave(PermissionRequiredMixin, views.View):
    permission_required = 'base.edit_content'

    def post(self, request):
        if 'name' in request.POST and 'content' in request.POST:
            try:
                obj = EditableContent.objects.get(name=request.POST['name'])
                obj.text = request.POST['content']
                obj.save()

                for image in obj.images.all():
                    if os.path.basename(image.image.name) not in obj.text:
                        image.image.delete(save=False)
                        image.delete()

                return JsonResponse({'success': True})
            except ObjectDoesNotExist:
                pass

        return JsonResponse({'success': False})


class EditableContentSaveImage(PermissionRequiredMixin, views.View):
    permission_required = 'base.edit_content'

    def post(self, request):
        if 'name' in request.POST and 'blobname' in request.POST:
            content = EditableContent.objects.get_or_create(name=request.POST['name'])[0]
            blob_name = request.POST['blobname']
            image = EditableContentImage(content=content, image=request.FILES[blob_name])
            image.save()

            return JsonResponse({'success': True, 'location': image.image.url})

        return JsonResponse({'success': False})
