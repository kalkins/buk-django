from datetime import date

from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO

from .models import Member, Instrument

test_member = {
    'email': 'test@example.com',
    'first_name': 'Test',
    'last_name': 'Testson',
    'joined_date': date(2017, 1, 1),
    'birthday': date(1996, 3, 5),
    'phone': '94857205',
    'address': 'Teststreet 42',
    'zip_code': '8472',
    'city': 'Testheim',
}


class MemberTestCase(TestCase):
    def setUp(self):
        test_member['instrument'] = Instrument.objects.create(name='Testolin')

    def test_create(self):
        member = Member.objects.create_user(**test_member)
        self.assertEqual(member.membership_periods.count(), 1)
        self.assertEqual(member.membership_periods.first().start, test_member['joined_date'])
        self.assertIsNone(member.membership_periods.first().end)

    def test_create_without_joined_date(self):
        local_test_member = dict(test_member)
        del local_test_member['joined_date']
        member = Member.objects.create(**local_test_member)
        self.assertEqual(member.membership_periods.count(), 0)

    def test_is_active(self):
        member = Member.objects.create_user(**test_member)
        self.assertTrue(member.is_active)
        period = member.membership_periods.first()
        period.end = date.today()
        period.save()
        self.assertFalse(member.is_active)
        member.membership_periods.create(start=date.today())
        self.assertTrue(member.is_active)
        period.end = date(2017, 2, 3)
        period.save()
        self.assertTrue(member.is_active)


class MakeSuperuserTestCase(TestCase):
    def setUp(self):
        test_member['instrument'] = Instrument.objects.create(name='Testolin')
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
