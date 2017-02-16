from django.test import TestCase
from .models import Member, Instrument

test_member = {
    'email': 'test@example.com',
    'first_name': 'Test',
    'last_name': 'Testson',
    'birthday': '1996-03-05',
    'phone': '94857205',
    'address': 'Teststreet 42',
    'zip_code': '8472',
    'city': 'Testheim',
}

class MemberTestCase(TestCase):
    def setUp(self):
        Instrument.objects.create(name='Testolin')

    def test_create_member(self):
        test_member['instrument'] = Instrument.objects.get(name='Testolin')
        Member.objects.create_user(**test_member)
