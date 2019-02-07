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
        null=True
    )
    loan_description = models.TextField('lånebeskrivelse', blank=True, default='')

    def __str__(self):
        return self.name


class UniformPiece(InventoryItem):
    size = models.CharField('størrelse', max_length=30)


class Pants(UniformPiece):
    def save(self):
        self.name = "Bukse størrelse " + self.size


class Jacket(UniformPiece):
    number = models.IntegerField('jakkenummer')

    def save(self):
        self.name = "Jakke nr. " + self.number


class Hat(UniformPiece):
    def save(self):
        self.name = "Hatt størrelse " + self.size


class Instrument(InventoryItem):
    pass
