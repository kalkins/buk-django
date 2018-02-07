import string
import random

from django.db import models
from django.core.exceptions import ValidationError


class Period(models.Model):
    """Store a period of time."""
    start = models.DateField('start')
    end = models.DateField('slutt', null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name = 'periode'
        verbose_name_plural = 'perioder'
        ordering = ['end', 'start']

    def clean(self):
        if self.end and self.end < self.start:
            raise ValidationError('En periode kan ikke slutte før den har startet.')

    def contains(self, date):
        return date >= self.start and (not self.end or date < self.end)

    def __str__(self):
        result = '%s - ' % self.start
        if self.end:
            result += str(self.end)
        return result


class EditableContent(models.Model):
    """
    Store content edited inline in TinyMCE.

    To use, include :template:`editable-content/editable-content.html`
    in the template, and import 'editable-content/js/tinymce/tinymce.min.js'
    and 'editable-content/js/content-editor.js'.

    See :model:`base.EditableContentImage` for information
    about storing images.
    """
    name = models.CharField(max_length=30, unique=True)
    text = models.TextField(blank=True, default='')

    class Meta:
        permissions = (
            ('edit_content', 'Kan redigere redigerbare områder'),
        )


def editable_content_image_path(instance, _):
    """
    Generates a random filename for :model:`base.EditableContentImage`
    to avoid conflicts.
    """
    filename = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)])
    return 'images/content_{0}/{1}'.format(instance.content.name, filename)


class EditableContentImage(models.Model):
    """
    Store images from inline content edited in TinyMCE.

    See :model:`base.EditableContent` for more information.
    """
    content = models.ForeignKey(
        EditableContent,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(
        upload_to=editable_content_image_path,
    )


class BaseComment(models.Model):
    """An abstract implementation of a comment."""
    poster = models.ForeignKey('members.Member', on_delete=models.CASCADE)
    comment = models.TextField('kommentar')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name = 'kommentar'
        verbose_name_plural = 'kommentarer'
        ordering = ('created',)

    def __str__(self):
        """Return the content of the comment."""
        return self.comment

    def get_absolute_url(self):
        return self.post.get_absolute_url()
