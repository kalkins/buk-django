from django.core.exceptions import ObjectDoesNotExist
from legacy.importers import LegacyImporter, ImportSkipRow
from django.db import connections
from .models import *
from datetime import date


class InstrumentImport(LegacyImporter):
    model = Instrument
    table = 'instrument'
    cols = {'name': 'instrument'}

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
        'joined_date': 'startetibuk_date',
        'quit_date': 'sluttetibuk_date',
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

    def convert_joined_date(self, val):
        if val:
            return val
        else:
            raise ImportSkipRow()

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

    def convert_about_me(self, val):
        return val if val else ''

    def convert_musical_background(self, val):
        return val if val else ''

    def ucreate_instance(self, params):
        defaults = params.pop('defaults')
        params = {**params, **defaults}

        is_active = params.pop('is_active')
        origin = params.pop('origin')
        occupation = params.pop('occupation')
        about_me = params.pop('about_me')
        musical_background = params.pop('musical_background')
        has_car = params.pop('has_car')
        has_towbar = params.pop('has_towbar')
        quit_date = params.pop('quit_date')

        try:
            obj = self.model.objects.get(email=params['email'])
            update = {}
            for col in self.update:
                update[col] = params[col]
            self.model.objects.filter(pk=obj.pk).update(**update)
        except ObjectDoesNotExist:
            obj = self.model.objects.create_user(**params)
        
        obj.is_active = is_active
        obj.origin = origin
        obj.occupation = occupation
        obj.about_me = about_me
        obj.musical_background = musical_background
        obj.has_car = has_car
        obj.has_towbar = has_towbar
        obj.quit_date = quit_date
        obj.save()
