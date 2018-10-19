from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser,
                                        PermissionsMixin, Group, Permission)

from base.models import Period


class InheritanceGroup(Group):
    """
    A group that allow inheritance of permissions.

    The groups that a group will inherit from is given
    by the `parents` field.

    The permissions that this group has independently
    from its parents are given by the `own_permissions` field.

    The standard `permissions` field will contain the groups own
    permissions, and those it has inherited. This field should not
    be altered, as any change will get overwritten.
    """

    parents = models.ManyToManyField(
        'self',
        related_name='sub_groups',
        symmetrical=False,
        blank=True,
        verbose_name='Overgrupper',
    )

    own_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name='Rettigheter',
    )

    def update_permissions(self):
        """Update the permissions of this and all sub groups."""
        permissions = list(self.own_permissions.all())

        for parent in self.parents.all():
            permissions += list(parent.permissions.all())

        self.permissions.set(permissions)

        for sub in self.sub_groups.all():
            sub.update_permissions()

    def get_sub_groups(self):
        """Return a queryset of all groups that inherits from this group."""
        subs = self.sub_groups.all()

        for sub in self.sub_groups.all():
            subs = subs.union(sub.get_sub_groups())

        return subs

    def get_all_parents(self):
        """Return a queryset of all groups that this group inherits from."""
        parents = self.parents.all()

        for parent in self.parents.all():
            parents = parents.union(parent.get_all_parents())

        return parents

    def get_available_parents(self):
        """
        Return a queryset of all groups that can be a parent to this group.

        This excludes any group that inherits from this group, as that would
        cause a circular dependency.
        """
        parents = InheritanceGroup.objects.exclude(pk=self.pk)
        for sub in self.get_sub_groups():
            parents = parents.exclude(pk=sub.pk)

        return parents


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


class PercussionGroup(models.Model):
    """Store a percussion carrying group."""
    name = models.CharField('navn', max_length=50, unique=True, editable=False)
    leader = models.OneToOneField(
        'Member',
        on_delete=models.PROTECT,
        null=True,
        related_name='percussion_group_leader_for',
        verbose_name='gruppeleder',
    )

    class Meta:
        verbose_name = 'slagverkbæregruppe'
        verbose_name_plural = 'slagverkbæregrupper'
        permissions = (
            ('change_percussion_group', 'Kan endre slagverkbæregrupper'),
        )
        ordering = ('name',)

    def __str__(self):
        return self.name

    def ordered_members(self):
        """
        Return a list of members of the group ordered by group leader,
        whether the member is on leave, first name and last name, in that order.
        """
        return self.members.all().order_by('percussion_group_leader_for', 'is_on_leave',
                                           'first_name', 'last_name')

    def save(self, *args, **kwargs):
        """
        Save the object to the database.

        If the objects is new a name is generated for it, on the form 'Gruppe <num>'.
        """
        if not self.name:
            self.name = 'Gruppe {}'.format(PercussionGroup.objects.count() + 1)

        super(PercussionGroup, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete the object, and rename other groups to fill the gap."""
        pk = self.pk
        prev = self.name
        super(PercussionGroup, self).delete(*args, **kwargs)

        for group in PercussionGroup.objects.filter(pk__gt=pk):
            tmp = group.name
            group.name = prev
            group.save()
            prev = tmp


class MemberManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, instrument, birthday,
                    phone, address, zip_code, city, password=None, joined_date=None):
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

        if joined_date:
            MembershipPeriod.objects.create(start=joined_date, member=user)

        return user

    def create_superuser(self, email, first_name, last_name, instrument,
                         birthday, phone, address, zip_code, city, password, joined_date=None):
        user = self.create_user(
                email, first_name, last_name, instrument,
                birthday, phone, address, zip_code, city, password, joined_date)

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
    percussion_group = models.ForeignKey(
        PercussionGroup,
        on_delete=models.SET_NULL,
        related_name='members',
        verbose_name='slagverkgruppe',
        blank=True,
        null=True,
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

    def save(self, *args, **kwargs):
        if self.pk:
            prev = Member.objects.get(pk=self.pk)
            if self.is_active != prev.is_active:
                self.percussion_group = None

                try:
                    group = self.percussion_group_leader_for
                    if group:
                        group.leader = None
                        group.save()
                except ObjectDoesNotExist:
                    pass

        super(Member, self).save(*args, **kwargs)

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


class BoardPosition(InheritanceGroup):
    """Store a member of the board (styret)."""
    holder = models.OneToOneField(
        Member,
        on_delete=models.PROTECT,
        related_name='board_position',
        verbose_name='innehaver',
    )
    description = models.TextField('beskrivelse', blank=True, default='')
    email = models.EmailField(
        verbose_name='e-post',
        max_length=255,
        unique=True,
    )
    order = models.IntegerField(
            'rekkefølge',
            default=0,
            help_text='Dette angir rekkefølgen styrevervene vises i. Lavere tall kommer først.')

    class Meta:
        verbose_name = 'styreverv'
        verbose_name_plural = 'styreverv'
        ordering = ('order',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Save the object to the database.

        Also add the related :model:`members.Member` to the
        group related to the board.
        """
        super(BoardPosition, self).save(*args, **kwargs)
        self.user_set.set([self.holder])


class Committee(InheritanceGroup):
    """
    Store a committee.

    A committee can be led by either a member on the board,
    or a regular member. Therefore one of these must be set,
    but not both.

    To get the :model:`members.Member` object of the leader,
    use the ``leader`` property.
    """
    leader_board = models.OneToOneField(
        BoardPosition,
        on_delete=models.PROTECT,
        verbose_name='leder i styret',
        related_name='committee_leader_of',
        blank=True,
        null=True,
        help_text='Lederen for komiteen. Denne eller den under må være satt, men ikke begge.',
    )
    leader_member = models.OneToOneField(
        Member,
        on_delete=models.PROTECT,
        verbose_name='leder medlem',
        related_name='committee_leader_of',
        blank=True,
        null=True,
    )
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

    @property
    def ordered_members(self):
        """
        Return a list of members of the committe ordered by leader,
        whether the member is on leave, first name and last name, in that order.
        """
        return self.user_set.all().order_by('committee_leader_of', 'is_on_leave',
                                            'first_name', 'last_name')

    @property
    def members(self):
        """Return the members of the committee, excluding the leader."""
        return self.user_set.exclude(pk=self.leader.pk)

    class Meta:
        verbose_name = 'komite'
        verbose_name_plural = 'komiteer'
        ordering = ('order',)

    def __str__(self):
        return self.name

    def clean(self):
        if not (self.leader_board_id or self.leader_member_id):
            raise ValidationError('En komite må ha en leder')
        elif self.leader_board and self.leader_member:
            raise ValidationError('En komite kan bare ha én leder')

    def save(self, *args, **kwargs):
        """Save the object to the database."""
        self.full_clean()
        super(Committee, self).save(*args, **kwargs)
        self.user_set.add(self.leader)
