from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser,
                                        PermissionsMixin, Group)

from base.models import Period


class Instrument(models.Model):
    """Store an instrument group."""
    name = models.CharField('navn', max_length=30, unique=True)
    group_leader = models.OneToOneField(
        'Member',
        on_delete=models.SET_NULL,
        verbose_name='gruppeleder',
        related_name='group_leader_for',
        blank=True,
        null=True,
    )
    order = models.IntegerField(
            'rekkefølge',
            default=0,
            help_text='Dette angir rekkefølgen instrumentene vises i. Lavere tall kommer først.')

    class Meta:
        verbose_name = 'instrument'
        verbose_name_plural = 'instrumenter'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MemberManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, joined_date, instrument,
                    birthday, phone, address, zip_code, city, password=None):
        # Allow the instrument parameter to be an object, the primary key, or the name
        if not isinstance(instrument, Instrument):
            try:
                instrument = Instrument.objects.get(pk=instrument)
            except ObjectDoesNotExist:
                try:
                    instrument = Instrument.objects.get(name=instrument)
                except ObjectDoesNotExist:
                    raise ValueError('Ugyldig instrument')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            instrument=instrument,
            birthday=birthday,
            phone=phone,
            address=address,
            zip_code=zip_code,
            city=city,
        )
        user.set_password(password)
        user.save(using=self._db)

        MembershipPeriod.objects.create(start=joined_date, member=user)

        return user

    def create_superuser(self, email, first_name, last_name, joined_date, instrument,
                         birthday, phone, address, zip_code, city, password):
        user = self.create_user(
                email, first_name, last_name, joined_date, instrument,
                birthday, phone, address, zip_code, city, password)

        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Member(AbstractBaseUser, PermissionsMixin):
    """
    Store a member.

    This replaces the standard user model, and uses
    :model:`members.MemberManager` as a custom manager.
    """
    email = models.EmailField(
        verbose_name='e-post',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField('aktiv', default=True)
    is_on_leave = models.BooleanField('i permisjon', default=False)
    is_admin = models.BooleanField('admin', default=False)
    first_name = models.CharField('fornavn', max_length=30)
    last_name = models.CharField('etternavn', max_length=30)
    phone = models.CharField('mobilnummer', max_length=20)
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.PROTECT,
        verbose_name='instrument',
        related_name='players',
    )
    birthday = models.DateField('fødselsdato', help_text='Datoer skrives på formen YYYY-MM-DD')
    address = models.CharField('adresse', max_length=60)
    zip_code = models.CharField('postnr.', max_length=4)
    city = models.CharField('poststed', max_length=40)
    origin = models.CharField('kommer fra', max_length=100, blank=True, default='')
    occupation = models.CharField('studie/yrke', max_length=255, blank=True, default='')
    about_me = models.TextField('litt om meg selv', blank=True, default='')
    musical_background = models.TextField('musikalsk bakgrunn', blank=True, default='')
    has_car = models.BooleanField('har bil', default=False)
    has_towbar = models.BooleanField('har hengerfeste', default=False)

    objects = MemberManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'instrument', 'birthday',
                       'address', 'zip_code', 'city']

    class Meta:
        verbose_name = 'medlem'
        verbose_name_plural = 'medlemmer'
        ordering = ['instrument', '-is_active', 'is_on_leave', 'group_leader_for',
                    'first_name', 'last_name']
        permissions = (
            ('statistics', 'Kan se statistikk for medlemmer'),
        )

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def status(self):
        """
        Return a string describing the members status.

        Can return 'Aktiv', 'Sluttet', or 'Permisjon'.
        """
        if self.is_on_leave:
            return 'Permisjon'
        elif self.is_active:
            return 'Aktiv'
        else:
            return 'Sluttet'

    def get_full_name(self):
        """Return the full name of the member."""
        return '%s %s' % (self.first_name, self.last_name)
    get_full_name.short_description = 'navn'

    def get_short_name(self):
        """Return first name of the member."""
        return self.first_name
    get_short_name.short_description = 'navn'

    def get_absolute_url(self):
        """Return a link to the members profile."""
        return reverse('member_detail', args=[str(self.pk)])

    def __str__(self):
        """Return the full name of the member."""
        return self.get_full_name()

    def is_group_leader(self):
        """
        Return a boolean describing whether the member
        is an instrument group leader.
        """
        return hasattr(self, 'group_leader_for')
    is_group_leader.short_description = 'er gruppeleder'

    def get_full_address(self):
        """
        Return the address of the member, containing the address,
        zip code and city.
        """
        return "%s %s %s" % (self.address, self.zip_code, self.city)
    get_full_address.short_description = 'adresse'


class MembershipPeriod(Period):
    """
    Store a :model:`base.Period` of membership for a :model:`member.Member`.
    """
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='membership_periods',
    )

    class Meta(Period.Meta):
        verbose_name = 'medlemskapsperiode'
        verbose_name_plural = 'medlemskapsperioder'

    def save(self, *args, **kwargs):
        """
        Save the object to the database, setting the ``is_active`` field
        of the related :model:`members.Member` in the process.
        """
        super(MembershipPeriod, self).save(*args, **kwargs)

        member = self.member

        # If there are open periods, i.e the member has not quit, the member is active
        member.is_active = member.membership_periods.filter(end=None).exists()
        member.save()


class LeavePeriod(Period):
    """
    Store a :model:`base.Period` of leave of absence for a :model:`member.Member`.
    """
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='leave_periods',
    )

    class Meta(Period.Meta):
        verbose_name = 'permisjonsperioder'
        verbose_name_plural = 'permisjonsperioder'

    def save(self, *args, **kwargs):
        """
        Save the object to the database, setting the ``is_on_leave`` field
        of the related :model:`members.Member` in the process.
        """
        super(LeavePeriod, self).save(*args, **kwargs)

        member = self.member
        member.is_on_leave = member.leave_periods.filter(end=None).exists()
        member.save()


class BoardPosition(models.Model):
    """Store a member of the board (styret)."""
    holder = models.OneToOneField(
        Member,
        on_delete=models.PROTECT,
        related_name='board_position',
        verbose_name='innehaver',
    )
    title = models.CharField('tittel', max_length=50, unique=True)
    description = models.TextField('beskrivelse', blank=True, default='')
    email = models.EmailField(
        verbose_name='e-post',
        max_length=255,
        unique=True,
    )
    group = models.OneToOneField(Group, editable=False, null=True)
    order = models.IntegerField(
            'rekkefølge',
            default=0,
            help_text='Dette angir rekkefølgen styrevervene vises i. Lavere tall kommer først.')

    class Meta:
        verbose_name = 'styreverv'
        verbose_name_plural = 'styreverv'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Save the object to the database.

        Also add the related :model:`members.Member` to the
        group related to the board.
        """
        board, _ = Group.objects.get_or_create(name='Styret')

        if not self.group:
            self.group = Group.objects.create(name=self.title)

        if self.pk:
            prev = BoardPosition.objects.get(pk=self.pk)
            if self.title != prev.title:
                self.group.update(name=self.title)
            if self.holder != prev.holder:
                board.user_set.remove(prev.holder)

        board.user_set.add(self.holder)

        super(BoardPosition, self).save(*args, **kwargs)

        self.group.user_set.set([self.holder])

    def delete(self, *args, **kwargs):
        """
        Delete the object, and remove the related
        :model:`members.Member` from the related group.
        """
        self.group.delete()
        Group.objects.get(name='Styret').user_set.remove(self.holder)
        super(BoardPosition, self).delete(*args, **kwargs)


class Committee(models.Model):
    """
    Store a committee.

    A committee can be led by either a member on the board,
    or a regular member. Therefore one of these must be set,
    but not both.

    To get the :model:`members.Member` object of the leader,
    use the ``leader`` property.
    """
    name = models.CharField('navn', max_length=50, unique=True)
    leader_board = models.OneToOneField(
        BoardPosition,
        on_delete=models.PROTECT,
        verbose_name='leder i styret',
        related_name='leader_of',
        blank=True,
        null=True,
        help_text='Lederen for komiteen. Denne eller den under må være satt, men ikke begge.',
    )
    leader_member = models.OneToOneField(
        Member,
        on_delete=models.PROTECT,
        verbose_name='leder medlem',
        related_name='leader_of',
        blank=True,
        null=True,
    )
    members = models.ManyToManyField(
        Member,
        verbose_name='medlemmer',
        related_name='committees',
        blank=True,
    )
    group = models.OneToOneField(Group, editable=False, null=True)
    email = models.EmailField(
        verbose_name='e-post',
        max_length=255,
        unique=True,
    )
    description = models.TextField('beskrivelse', blank=True, default='')
    order = models.IntegerField(
            'rekkefølge',
            default=0,
            help_text='Dette angir rekkefølgen komiteene vises i. Lavere tall kommer først.')

    # Use this to get the member object of the leader of the group. Use leader_board
    # to see the associated board position (if it is set)
    @property
    def leader(self):
        """Return the :model:`members.Member` object of the leader."""
        return self.leader_board.holder if self.leader_board_id else self.leader_member
    leader.fget.short_description = 'leder'

    class Meta:
        verbose_name = 'komite'
        verbose_name_plural = 'komiteer'

    def __str__(self):
        return self.name

    def clean(self):
        if not (self.leader_board_id or self.leader_member_id):
            raise ValidationError('En komite må ha en leder')
        if self.leader_board:
            self.leader_member = None

    def save(self, *args, **kwargs):
        """
        Save the object to the database, adding its members
        to the related group in the process.

        If there's no related group, one is created with the
        same name as the committee.
        """
        if self.group:
            if self.pk:
                prev = Committee.objects.get(pk=self.pk)
                if self.name != prev.name:
                    self.group.update(name=self.name)
        else:
            self.group = Group.objects.create(name=self.name)

        super(Committee, self).save(*args, **kwargs)

        self.group.user_set.set(self.members.all())
        self.group.user_set.add(self.leader)
        self.members.remove(self.leader)

    def delete(self, *args, **kwargs):
        """Delete the committee and the related group."""
        self.group.delete()
        super(Committee, self).delete(*args, **kwargs)
