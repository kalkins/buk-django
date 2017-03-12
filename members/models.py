from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group
from django.urls import reverse

from datetime import date

class Instrument(models.Model):
    name = models.CharField('navn', max_length=30, unique=True)
    group_leader = models.OneToOneField(
        'Member',
        on_delete = models.SET_NULL,
        verbose_name = 'gruppeleder',
        related_name = 'group_leader_for',
        blank = True,
        null = True,
    )
    order = models.IntegerField('rekkefølge', default=0,
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
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            joined_date = joined_date,
            instrument = instrument,
            birthday = birthday,
            phone = phone,
            address = address,
            zip_code = zip_code,
            city = city,
        )
        user.set_password(password)
        user.save(using=self._db)

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
    email = models.EmailField(
        verbose_name = 'e-post',
        max_length = 255,
        unique = True,
    )
    is_active = models.BooleanField('aktiv', default=True)
    is_admin = models.BooleanField('admin', default=False)
    first_name = models.CharField('fornavn', max_length=30)
    last_name = models.CharField('etternavn', max_length=30)
    phone = models.CharField('mobilnummer', max_length=20)
    instrument = models.ForeignKey(
        Instrument,
        on_delete = models.PROTECT,
        verbose_name = 'instrument',
        related_name = 'players',
    )
    birthday = models.DateField('fødselsdato', help_text='Datoer skrives på formen YYYY-MM-DD')
    joined_date = models.DateField('startet i BUK', default=date.today,
            help_text='Datoer skrives på formen YYYY-MM-DD')
    quit_date = models.DateField('sluttet i BUK', null=True, blank=True, default=None,
            help_text='Datoer skrives på formen YYYY-MM-DD')
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
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'instrument', 'birthday', 'joined_date',
            'address', 'zip_code', 'city']

    class Meta:
        verbose_name = 'medlem'
        verbose_name_plural = 'medlemmer'
        ordering = ['instrument', 'is_active', 'group_leader_for', 'first_name']

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def status(self):
        return 'Aktiv' if self.is_active else 'Sluttet'

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    get_full_name.short_description = 'navn'

    def get_short_name(self):
        return self.first_name
    get_short_name.short_description = 'navn'

    def get_absolute_url(self):
        return reverse('member_detail', args=[str(self.pk)])

    def __str__(self):
        return self.get_full_name()

    def is_group_leader(self):
        return hasattr(self, 'group_leader_for')
    is_group_leader.short_description = 'er gruppeleder'

    def get_full_address(self):
        return "%s %s %s" % (self.address, self.zip_code, self.city)
    get_full_address.short_description = 'adresse'

    def save(self, *args, **kwargs):
        if self.pk:
            prev = Member.objects.get(pk=self.pk)
            # If the member has just been rendered inactive,
            # but the quit date isn't set, set it to today
            # If the user is becoming active, clear the quit date.
            if prev.is_active != self.is_active:
                if self.is_active:
                    self.quit_date = None
                elif not self.quit_date:
                    self.quit_date = date.today()
        elif not self.joined_date:
            # If it's a new member that doesn't have a joined date,
            # set it to today
            self.joined_date = date.today()

        super(Member, self).save(*args, **kwargs)


class BoardPosition(models.Model):
    holder = models.OneToOneField(
        Member,
        on_delete = models.PROTECT,
        verbose_name = 'innehaver',
    )
    title = models.CharField('tittel', max_length=50, unique=True)
    description = models.TextField('beskrivelse', blank=True, default='')
    email = models.EmailField(
        verbose_name = 'e-post',
        max_length = 255,
        unique = True,
    )
    group = models.OneToOneField(Group, editable=False, null=True)
    order = models.IntegerField('rekkefølge', default=0,
            help_text='Dette angir rekkefølgen styrevervene vises i. Lavere tall kommer først.')

    class Meta:
        verbose_name = 'styreverv'
        verbose_name_plural = 'styreverv'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
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
        self.group.delete()
        Group.objects.get(name='Styret').user_set.remove(self.holder)
        super(BoardPosition, self).delete(*args, **kwargs)


class Committee(models.Model):
    name = models.CharField('navn', max_length=50, unique=True)
    # A committee can be led by either a member on the board, or a regular member.
    # Therefore one of these must be set, but not both
    leader_board = models.OneToOneField(
        BoardPosition,
        on_delete = models.PROTECT,
        verbose_name = 'leder i styret',
        related_name = 'leader_of',
        blank = True,
        null = True,
        help_text = 'Lederen for komiteen. Denne eller den under må være satt, men ikke begge.',
    )
    leader_member = models.OneToOneField(
        Member,
        on_delete = models.PROTECT,
        verbose_name = 'leder medlem',
        related_name = 'leader_of',
        blank = True,
        null = True,
    )
    members = models.ManyToManyField(
        Member,
        verbose_name = 'medlemmer',
        related_name = 'committees',
        blank = True,
    )
    group = models.OneToOneField(Group, editable=False, null=True)
    email = models.EmailField(
        verbose_name = 'e-post',
        max_length = 255,
        unique = True,
    )
    description = models.TextField('beskrivelse', blank=True, default='')
    order = models.IntegerField('rekkefølge', default=0,
            help_text='Dette angir rekkefølgen komiteene vises i. Lavere tall kommer først.')

    # Use this to get the member object of the leader of the group. Use leader_board
    # to see the associated board position (if it is set)
    @property
    def leader(self):
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
            self.leader_member = None;

    def save(self, *args, **kwargs):
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
        self.group.delete()
        super(Committee, self).delete(*args, **kwargs)
