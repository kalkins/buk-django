from django.db import models
from django.core.exceptions import ValidationError


class Period(models.Model):
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
    name = models.CharField(max_length=30)
    text = models.TextField(blank=True, default='')

    class Meta:
        permissions = (
            ('edit_content', 'Kan redigere redigerbare områder'),
        )


def editable_content_image_path(instance, filename):
    return 'images/content_{0}/{1}'.format(instance.content.name, filename)

class EditableContentImage(models.Model):
    content = models.ForeignKey(
        EditableContent,
        on_delete = models.CASCADE,
    )
    image = models.ImageField(
        upload_to = editable_content_image_path,
    )
