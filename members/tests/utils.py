from datetime import date

from base.tests import random_string
from ..models import Member, Instrument


def generate_member_attrs(**kwargs):
    """
    Generate the attributes needed to create a member.

    If you need the member to have custom attributes
    you can pass them as keyword parameters.

    If no email is provided a random one is generated.

    If no instrument is provided the first available is
    choosen, or one is created if no instruments exists.
    """
    test_member = {
        'email': f'{random_string(5)}@{random_string(7)}.com',
        'first_name': 'Test',
        'last_name': 'Testson',
        'joined_date': date(2017, 1, 1),
        'birthday': date(1996, 3, 5),
        'phone': '94857205',
        'address': 'Teststreet 42',
        'zip_code': '8472',
        'city': 'Testheim',
        **kwargs,
    }

    if 'instrument' not in test_member:
        test_member['instrument'] = Instrument.objects.first() if Instrument.objects.count() else Instrument.objects.create(name='Generated instrument')

    return test_member


def generate_member(**kwargs):
    """Same as generate_member_attrs, but actually creates and returns the member"""
    return Member.objects.create_user(**generate_member_attrs(**kwargs))
