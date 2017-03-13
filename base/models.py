from django.db import models


class Period(models.Model):
    start = models.DateField('start')
    end = models.DateField('slutt', null=True)

    class Meta:
        abstract = True
        verbose_name = 'periode'
        verbose_name_plural = 'perioder'
        ordering = ['end', 'start']

    def contains(self, date):
        return date >= self.start and (not self.end or date < self.end)

    def __str__(self):
        result = '%s - ' % self.start
        if self.end:
            result += str(self.end)
        return result
