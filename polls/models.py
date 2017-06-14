from django.db import models
from django.urls import reverse

from members.models import Member, Instrument


class Poll(models.Model):
    """
    Store a poll which users can answer.

    The options are dynamic, and stored in
    :model:`members.PollOption`.
    """
    title = models.CharField('tittel', max_length=50, blank=True)
    deadline = models.DateTimeField('frist', null=True, blank=True)

    class Meta:
        verbose_name = 'påmelding'
        verbose_name_plural = 'påmeldinger'

    def __str__(self):
        """Return the title of the poll."""
        return self.title

    def get_absolute_url(self):
        """Return a link to the members profile."""
        return reverse('poll_statistics', args=[str(self.pk)])


class PollOption(models.Model):
    """
    Store an option for a :model:`members.Poll`,
    and the users that choose it.
    """
    poll = models.ForeignKey(Poll, related_name='options')
    members = models.ManyToManyField(Member)
    title = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'valg'
        verbose_name_plural = 'valg'

    def __str__(self):
        """Return the title of the option."""
        return self.title

    def instruments(self):
        """
        Return the amount of members of each instrument that chose this option.
        """
        result = []

        for instrument in Instrument.objects.all():
            count = self.members.filter(instrument=instrument).count()
            if count:
                result.append({'name': instrument.name, 'count': count})

        return result
