from django.db import models
from django.urls import reverse
from model_utils.managers import InheritanceManager

from base.models import Period
from base.model_fields import CustomManyToManyField, CustomDateTimeField
from members.models import Member, PercussionGroup


class Activity(models.Model):
    objects = InheritanceManager()

    PUBLIC = 'PUB'
    INTERNAL = 'INT'
    ADMIN = 'ADM'

    visibility_choices = (
        (PUBLIC, 'Offentlig'),
        (INTERNAL, 'Intern'),
        (ADMIN, 'Admin'),
    )

    title = models.CharField('tittel', max_length=150)
    visibility = models.CharField('synlighet', max_length=3, choices=visibility_choices)
    description = models.TextField('beskrivelse', blank=True)
    description_internal = models.TextField('intern beskrivelse',
                                            help_text='Vises bare for innloggede medlemmer',
                                            blank=True)
    location = models.CharField('sted', max_length=150)
    bakers = CustomManyToManyField(
        Member,
        verbose_name='kakebakere',
        related_name='baker_for',
        blank=True,
    )
    percussion_group = models.ForeignKey(
        PercussionGroup,
        on_delete=models.SET_NULL,
        verbose_name='slagsverksbæregruppe',
        related_name='activities',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'aktivitet'
        verbose_name_plural = 'aktiviteter'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('activity_detail', args=[str(self.pk)])


class Rehearsal(Activity):
    class Meta:
        verbose_name = 'øvelse'
        verbose_name_plural = 'øvelser'


class Concert(Activity):
    price = models.PositiveIntegerField('pris vanlig')
    price_student = models.PositiveIntegerField('pris student')

    class Meta:
        verbose_name = 'konsert'
        verbose_name_plural = 'konserter'


class Other(Activity):
    class Meta:
        verbose_name = 'annet'
        verbose_name_plural = 'annet'


class ActivityPeriod(Period):
    start = CustomDateTimeField('start')
    end = CustomDateTimeField('slutt', null=True, blank=True)

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='periods',
    )
