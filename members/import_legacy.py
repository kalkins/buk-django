from django.core.exceptions import ObjectDoesNotExist
from legacy.importers import LegacyImporter, ImportSkipRow
from django.db import connections
from .models import *
from datetime import date


class InstrumentImport(LegacyImporter):
    model = Instrument
    table = 'instrument'
    cols = {
        'name': 'instrument',
        'order': 'instrumentid',
    }
    check = ['name']

    def convert_name(self, val):
        if val == 'Støttemedlem' or val == 'Æresmedlem':
            raise ImportSkipRow()
        return val


class MemberImport(LegacyImporter):
    model = Member
    table = 'medlemmer'
    cols = {
        'email': 'email',
        'is_active': 'status',
        'first_name': 'fnavn',
        'last_name': 'enavn',
        'phone': ['tlfprivat', 'tlfmobil', 'tlfarbeid'],
        'instrument': ['instrument', 'instnr'],
        'birthday': 'fdato',
        'address': 'adresse',
        'zip_code': 'postnr',
        'city': 'poststed',
        'origin': 'kommerfra',
        'occupation': 'studieyrke',
        'about_me': 'ommegselv',
        'musical_background': 'bakgrunn',
        'has_car': 'bil',
        'has_towbar': 'hengerfeste',
    }
    check = ['email']
    manytomany = ['membership_periods']

    def convert_email(self, val):
        if val == '':
            raise ImportSkipRow
        return val

    def convert_phone(self, tlfmobil, tlfarbeid, tlfprivat):
        if tlfprivat:
            return tlfprivat
        elif tlfmobil:
            return tlfmobil
        elif tlfarbeid:
            return tlfarbeid
        else:
            return '55555555'

    def convert_birthday(self, val):
        return val if val else date(1970, 1, 1)

    def convert_is_active(self, val):
        return val == 'Aktiv' or val == 'Permisjon'

    def convert_instrument(self, val):
        name = val['instrument']
        nr = val['instnr']

        if nr:
            sql = 'SELECT instrument FROM instrument WHERE instrumentid = %d' % nr
            cursor = connections[self.db].cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            name = row[0]

        if name and name != 'Støttemedlem' and name != 'Æresmedlem':
            # get_or_create returns the object, and a status code which we ignore
            return Instrument.objects.get_or_create(name=name)[0]

        raise ImportSkipRow()

    def convert_city(self, val):
        return val if val else 'Ukjent'

    def convert_origin(self, val):
        return val if val else 'Ukjent'

    def convert_occupation(self, val):
        return val if val else 'Ukjent'

    def convert_about_me(self, val):
        return val if val else ''

    def convert_musical_background(self, val):
        return val if val else ''


class MembershipPeriodImport(LegacyImporter):
    model = MembershipPeriod
    table = 'medlemmer'
    cols = {
        'start': 'startetibuk_date',
        'end': 'sluttetibuk_date',
        'member': 'email',
    }
    check = ['member']

    def convert_start(self, val):
        if not val:
            raise ImportSkipRow()
        return val

    def convert_member(self, val):
        members = Member.objects.filter(email=val)
        if len(members) == 1:
            return members[0]
        raise ImportSkipRow()


class LeavePeriodImport(LegacyImporter):
    model = LeavePeriod
    table = 'medlemmer'
    cols = {
        'start': 'status',
        'member': 'email',
    }
    check = ['member']

    # The old database didn't record when members went on leave, so we
    # just have to set a random startdate and fix it later.
    def convert_start(self, val):
        if val == 'Permisjon':
            return date.today()
        else:
            raise ImportSkipRow()

    def convert_member(self, val):
        members = Member.objects.filter(email=val)
        if len(members) == 1:
            return members[0]
        raise ImportSkipRow()
