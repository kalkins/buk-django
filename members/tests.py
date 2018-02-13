import random
import string
from datetime import date

from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO
from django.contrib.auth.models import Group

from .models import Member, Instrument, PercussionGroup, BoardPosition

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


def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def generate_member():
    local_test_member = dict(test_member)
    local_test_member['email'] = '{}@{}.com'.format(random_string(5), random_string(7))
    return Member.objects.create_user(**local_test_member)


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


class PercussionGroupTestCase(TestCase):
    cls = PercussionGroup

    def setUp(self):
        test_member['instrument'] = Instrument.objects.create(name='Testolin')

    def get_leader(self):
        return generate_member()

    def test_add_groups(self):
        group1 = self.cls(leader=self.get_leader())
        group1.save()
        self.assertEqual(group1.name, 'Gruppe 1')

        group2 = self.cls(leader=self.get_leader())
        group2.save()
        self.assertEqual(group2.name, 'Gruppe 2')

    def test_without_leader(self):
        group1 = self.cls()
        group1.save()
        self.assertEqual(group1.name, 'Gruppe 1')

        group2 = self.cls()
        group2.save()
        self.assertEqual(group2.name, 'Gruppe 2')

    def test_remove_groups(self):
        group1 = self.cls(leader=self.get_leader())
        group1.save()
        group2 = self.cls(leader=self.get_leader())
        group2.save()
        group3 = self.cls(leader=self.get_leader())
        group3.save()

        self.assertEqual(group3.name, 'Gruppe 3')
        group2.delete()
        group3.refresh_from_db()
        self.assertEqual(group3.name, 'Gruppe 2')

    def test_delete_and_add(self):
        group1 = self.cls(leader=self.get_leader())
        group1.save()
        group2 = self.cls(leader=self.get_leader())
        group2.save()
        group3 = self.cls(leader=self.get_leader())
        group3.save()

        self.assertEqual(group3.name, 'Gruppe 3')
        group3.delete()

        group4 = self.cls(leader=self.get_leader())
        group4.save()
        self.assertEqual(group4.name, 'Gruppe 3')

    def test_member_quit(self):
        group = self.cls()
        group.save()

        member = generate_member()
        member.percussion_group = group
        member.save()

        self.assertEqual(group.members.count(), 1)

        member.is_active = False
        member.save()

        self.assertEqual(group.members.count(), 0)

    def test_leader_quit(self):
        member = generate_member()
        member.save()

        group = self.cls(leader=member)
        group.save()

        self.assertEqual(group.leader, member)

        member.is_active = False
        member.save()

        group.refresh_from_db()
        self.assertIsNone(group.leader)

class BoardPositionTestCase(TestCase):
    def setUp(self):
        test_member['instrument'] = Instrument.objects.create(name='Testolin')

    def test_str(self):
        holder = generate_member();

        board_position = BoardPosition(title="Testansvarlig", holder=holder)
        self.assertEqual(board_position.__str__(), "Testansvarlig")

    def test_holder(self):
        holder = generate_member()

        board_position = BoardPosition(title="Testansvarlig", holder=holder)
        self.assertEqual(holder, board_position.holder)

    def test_added_to_group(self):
        holder = generate_member()
        board_position = BoardPosition(title="Testansvarlig", holder=holder)
        board_position.save()

        group = Member.objects.filter(groups__name="Testansvarlig")
        self.assertEqual(holder in group, True)

    def test_added_to_board_group(self):
        holder = generate_member()
        board_position = BoardPosition(title="Testansvarlig", holder=holder)
        board_position.save()

        board = Member.objects.filter(groups__name="Styret")
        self.assertEqual(holder in board, True)

    def test_delete(self):
        holder = generate_member()
        board_position = BoardPosition(title="Testansvarlig", holder=holder)
        board_position.save()
        board_position.delete()

        board = Member.objects.filter(groups__name="Styret")
        self.assertEqual(holder in board, False)

        group = Member.objects.filter(groups__name="Testansvarlig")
        #self.assertEqual(holder in group, False)

    def test_new_holder(self):
        holder = generate_member()
        board_position = BoardPosition(title="Testansvarlig", holder=holder)
        board_position.save()

        new_holder = generate_member();
        board_position.holder = new_holder
        board_position.save()

        board = Member.objects.filter(groups__name="Styret")
        self.assertEqual(holder in board, False);
        self.assertEqual(new_holder in board, True);

        group = Member.objects.filter(groups__name="Testansvarlig")
        self.assertEqual(holder in group, False)
        self.assertEqual(new_holder in group, True)

        """
    def test_new_title(self):
        holder = generate_member()
        board_position = BoardPosition(title="Testansvarlig", holder=holder)
        board_position.save()

        board_position.title="TestMaster"
        board_position.save()

        group = Member.objects.filter(groups__name="Testansvarlig")
        self.assertEqual(holder in group, False)

        group = Member.objects.filter(groups__name="TestMaster")
        self.assertEqual(holder in group, True)
        """
