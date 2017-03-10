from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO
from .models import Member, Instrument

test_member = {
    'email': 'test@example.com',
    'first_name': 'Test',
    'last_name': 'Testson',
    'joined_date': '2017-01-01',
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


class MakeSuperuserTestCase(TestCase):
    def setUp(self):
        Instrument.objects.create(name='Testolin')
        test_member['instrument'] = Instrument.objects.get(name='Testolin')
        self.member = Member.objects.create_user(**test_member)

    def test_failure(self):
        email = 'test@testcase.test'
        err = StringIO()
        call_command('makesuperuser', email, stderr=err)
        self.assertIn('No member with email %s' % email, err.getvalue())

    def test_adding(self):
        self.assertFalse(self.member.is_admin)
        self.assertFalse(self.member.is_superuser)

        call_command('makesuperuser', self.member.email)
        self.member.refresh_from_db()

        self.assertTrue(self.member.is_admin)
        self.assertTrue(self.member.is_superuser)

    def test_removing(self):
        self.assertFalse(self.member.is_admin)
        self.assertFalse(self.member.is_superuser)

        call_command('makesuperuser', self.member.email, remove=True)
        self.member.refresh_from_db()

        self.assertFalse(self.member.is_admin)
        self.assertFalse(self.member.is_superuser)

    def test_output_adding(self):
        out = StringIO()
        call_command('makesuperuser', self.member.email, stdout=out)
        self.assertIn('%s added as superuser' % self.member.get_full_name(), out.getvalue())

    def test_output_removing(self):
        out = StringIO()
        call_command('makesuperuser', self.member.email, remove=True, stdout=out)
        self.assertIn('%s removed as superuser' % self.member.get_full_name(), out.getvalue())
