from django.db import models
from members.models import Member


class InventoryItem(models.Model):
    name = models.CharField('navn', max_length=30)
    description = models.TextField('beskrivelse', blank=True, default='')
    loaned_out = models.BooleanField(default=False)
    loaned_to_member = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        verbose_name="loaned_to",
        related_name="loaned_from",
        null=True,
        blank=True
    )
    loan_description = models.TextField('lånebeskrivelse', blank=True, default='')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class UniformPiece(InventoryItem):
    size = models.CharField('størrelse', max_length=30)


class Pants(UniformPiece):
    def save(self, *args, **kwargs):
        self.name = "Bukse størrelse " + self.size
        super(Pants, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'bukse'
        verbose_name_plural = 'bukser'


class Jacket(UniformPiece):
    number = models.IntegerField('jakkenummer')

    def save(self, *args, **kwargs):
        self.name = "Jakke nr. " + self.number
        super(Jacket, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'jakke'
        verbose_name_plural = 'jakker'


class Hat(UniformPiece):
    def save(self, *args, **kwargs):
        self.name = "Hatt størrelse " + self.size
        super(Hat, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'hatt'
        verbose_name_plural = 'hatter'


class Instrument(InventoryItem):
    class Meta:
        verbose_name = 'instrument'
        verbose_name_plural = 'instrumenter'
