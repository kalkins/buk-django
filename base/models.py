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
