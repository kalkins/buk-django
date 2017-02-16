from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.core.exceptions import ObjectDoesNotExist

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

    class Meta:
        verbose_name = 'instrument'
        verbose_name_plural = 'instrumenter'

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
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class Member(AbstractUser):
    email = models.EmailField(
        verbose_name = 'e-post',
        max_length = 255,
        unique = True,
    )
    is_active = models.BooleanField('aktiv', default=True)
    is_admin = models.BooleanField(default=False)
    first_name = models.CharField('fornavn', max_length=30)
    last_name = models.CharField('etternavn', max_length=30)
    phone = models.CharField('mobilnummer', max_length=20)
    instrument = models.ForeignKey(
        Instrument,
        on_delete = models.PROTECT,
        verbose_name = 'instrument',
        related_name = 'members',
    )
    birthday = models.DateField('fødselsdato', help_text='Datoer skrives på formen YYYY-MM-DD')
    joined_date = models.DateField('startet i BUK', default=date.today,
            help_text='Datoer skrives på formen YYYY-MM-DD')
    quit_date = models.DateField('sluttet i BUK', null=True, blank=True, default=None,
            help_text='Datoer skrives på formen YYYY-MM-DD')
    address = models.CharField('adresse', max_length=60)
    zip_code = models.CharField('postnr.', max_length=4)
    city = models.CharField('poststed', max_length=40)
    origin = models.CharField('kommer fra', max_length=50, blank=True, default='')
    occupation = models.CharField('studie/yrke', max_length=100, blank=True, default='')
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

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    get_full_name.short_description = 'navn'

    def get_short_name(self):
        return self.first_name
    get_short_name.short_description = 'navn'

    def __str__(self):
        return self.get_full_name()

    def is_group_leader(self):
        return hasattr(self.user, 'group_leader_for')
    is_group_leader.short_description = 'er gruppeleder'

    def get_full_address(self):
        return "%s %s %s" % (self.address, self.zip_code, self.city)
    get_full_address.short_description = 'adresse'
