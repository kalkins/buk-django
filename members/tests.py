import random
import string
from datetime import date

from django.test import TestCase
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.utils.six import StringIO
from django.db.utils import IntegrityError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import Member, Instrument, PercussionGroup, BoardPosition, InheritanceGroup, Committee

def random_string(length):
    return ''.join(random.choices(string.ascii_uppercase, k=length))

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


def permission_to_perm(permission):
    """Find the <app_label>.<codename> string for a permission object"""
    return '.'.join([permission.content_type.app_label, permission.codename])


class MemberTestCase(TestCase):
    def test_create(self):
        attrs = generate_member_attrs()
        member = Member.objects.create_user(**attrs)
        self.assertEqual(member.membership_periods.count(), 1)
        self.assertEqual(member.membership_periods.first().start, attrs['joined_date'])
        self.assertIsNone(member.membership_periods.first().end)

    def test_create_without_joined_date(self):
        member = generate_member(joined_date=None)
        self.assertEqual(member.membership_periods.count(), 0)

    def test_is_active(self):
        member = generate_member()
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
        self.member = generate_member()

    def test_failure(self):
        email = 'test@testcase.test'
        err = StringIO()
        call_command('makesuperuser', email, stderr=err)
        self.assertIn('No member with email %s' % email, err.getvalue())

    def test_adding(self):
        self.assertFalse(self.member.is_admin)
        self.assertFalse(self.member.is_superuser)

        call_command('makesuperuser', self.member.email, stdout=StringIO())
        self.member.refresh_from_db()

        self.assertTrue(self.member.is_admin)
        self.assertTrue(self.member.is_superuser)

    def test_removing(self):
        self.assertFalse(self.member.is_admin)
        self.assertFalse(self.member.is_superuser)

        call_command('makesuperuser', self.member.email, remove=True, stdout=StringIO())
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


class InheritanceGroupTestCase(TestCase):
    def setUp(self):
        org = InheritanceGroup.objects.create(name='Org')
        mentor = InheritanceGroup.objects.create(name='Mentor')
        mentor.parents.add(org)
        dev = InheritanceGroup.objects.create(name='Dev')
        dev.parents.add(org)
        arr = InheritanceGroup.objects.create(name='Arrangement')
        arr.parents.add(org)
        InheritanceGroup.objects.create(name='Leder').parents.add(mentor, dev, arr)

        content_type = ContentType.objects.get_for_model(Member)
        for i in range(5):
            Permission.objects.create(
                codename='perm{}'.format(i),
                name='Perm {}'.format(i),
                content_type=content_type,
            )

    def test_update_single_parent(self):
        org = InheritanceGroup.objects.get(name='Org')
        dev = InheritanceGroup.objects.get(name='Dev')
        perm1 = Permission.objects.get(codename='perm1')

        org.own_permissions.add(perm1)

        self.assertIn(perm1, org.permissions.all())
        self.assertIn(perm1, dev.permissions.all())

        org.own_permissions.remove(perm1)

        self.assertNotIn(perm1, org.permissions.all())
        self.assertNotIn(perm1, dev.permissions.all())

        dev.own_permissions.add(perm1)

        self.assertNotIn(perm1, org.permissions.all())
        self.assertIn(perm1, dev.permissions.all())

        dev.own_permissions.clear()

        self.assertNotIn(perm1, org.permissions.all())
        self.assertNotIn(perm1, dev.permissions.all())

    def test_update_multiple_parents(self):
        org = InheritanceGroup.objects.get(name='Org')
        dev = InheritanceGroup.objects.get(name='Dev')
        mentor = InheritanceGroup.objects.get(name='Mentor')
        leder = InheritanceGroup.objects.get(name='Leder')

        perm1 = Permission.objects.get(codename='perm1')
        perm2 = Permission.objects.get(codename='perm2')
        perm3 = Permission.objects.get(codename='perm3')
        perm4 = Permission.objects.get(codename='perm4')

        org.own_permissions.add(perm1)
        dev.own_permissions.add(perm2)
        mentor.own_permissions.add(perm3)
        leder.own_permissions.add(perm4)

        self.assertIn(perm1, org.permissions.all())
        self.assertIn(perm1, dev.permissions.all())
        self.assertIn(perm1, mentor.permissions.all())
        self.assertIn(perm1, leder.permissions.all())

        self.assertNotIn(perm2, org.permissions.all())
        self.assertIn(perm2, dev.permissions.all())
        self.assertNotIn(perm2, mentor.permissions.all())
        self.assertIn(perm2, leder.permissions.all())

        self.assertNotIn(perm3, org.permissions.all())
        self.assertNotIn(perm3, dev.permissions.all())
        self.assertIn(perm3, mentor.permissions.all())
        self.assertIn(perm3, leder.permissions.all())

        self.assertNotIn(perm4, org.permissions.all())
        self.assertNotIn(perm4, dev.permissions.all())
        self.assertNotIn(perm4, mentor.permissions.all())
        self.assertIn(perm4, leder.permissions.all())

        mentor.own_permissions.remove(perm3)

        self.assertNotIn(perm3, org.permissions.all())
        self.assertNotIn(perm3, dev.permissions.all())
        self.assertNotIn(perm3, mentor.permissions.all())
        self.assertNotIn(perm3, leder.permissions.all())

        org.own_permissions.clear()

        self.assertNotIn(perm1, org.permissions.all())
        self.assertNotIn(perm1, dev.permissions.all())
        self.assertNotIn(perm1, mentor.permissions.all())
        self.assertNotIn(perm1, leder.permissions.all())

    def test_add_group(self):
        org = InheritanceGroup.objects.get(name='Org')
        dev = InheritanceGroup.objects.get(name='Dev')
        perm1 = Permission.objects.get(codename='perm1')
        perm2 = Permission.objects.get(codename='perm2')

        org.own_permissions.add(perm1)
        dev.own_permissions.add(perm2)

        new_group = InheritanceGroup.objects.create(name='new-group')
        new_group.parents.add(dev)

        self.assertIn(perm1, new_group.permissions.all())
        self.assertIn(perm2, new_group.permissions.all())

    def test_user(self):
        org = InheritanceGroup.objects.get(name='Org')
        dev = InheritanceGroup.objects.get(name='Dev')
        perm1 = Permission.objects.get(codename='perm1')
        perm2 = Permission.objects.get(codename='perm2')
        perm1_str = permission_to_perm(perm1)
        perm2_str = permission_to_perm(perm2)
        org.own_permissions.add(perm1)

        user1 = generate_member()
        user2 = generate_member()

        user1.groups.add(org)
        user2.groups.add(dev)
        dev.own_permissions.add(perm2)
        self.assertTrue(user1.has_perm(perm1_str))
        self.assertFalse(user1.has_perm(perm2_str))
        self.assertTrue(user2.has_perm(perm1_str))
        self.assertTrue(user2.has_perm(perm2_str))

    def test_get_sub_group(self):
        org = InheritanceGroup.objects.get(name='Org')
        arr = InheritanceGroup.objects.get(name='Arrangement')
        dev = InheritanceGroup.objects.get(name='Dev')
        web = InheritanceGroup.objects.create(name='Web')
        web.parents.add(dev)

        self.assertIn(dev, org.get_sub_groups())
        self.assertIn(arr, org.get_sub_groups())
        self.assertIn(web, org.get_sub_groups())
        self.assertIn(web, dev.get_sub_groups())
        self.assertNotIn(arr, dev.get_sub_groups())
        self.assertNotIn(dev, arr.get_sub_groups())

    def test_get_all_parents(self):
        org = InheritanceGroup.objects.get(name='Org')
        arr = InheritanceGroup.objects.get(name='Arrangement')
        dev = InheritanceGroup.objects.get(name='Dev')
        web = InheritanceGroup.objects.create(name='Web')
        web.parents.add(dev)

        self.assertIn(dev, web.get_all_parents())
        self.assertIn(org, web.get_all_parents())
        self.assertNotIn(arr, web.get_all_parents())
        self.assertNotIn(web, arr.get_all_parents())

    def test_get_available_parents(self):
        org = InheritanceGroup.objects.get(name='Org')
        arr = InheritanceGroup.objects.get(name='Arrangement')
        mentor = InheritanceGroup.objects.get(name='Mentor')
        dev = InheritanceGroup.objects.get(name='Dev')
        web = InheritanceGroup.objects.create(name='Web')
        web.parents.add(dev)
        misc = InheritanceGroup.objects.create(name='Misc')

        self.assertEqual(org.get_available_parents().count(), 1)
        self.assertIn(misc, org.get_available_parents().all())

        self.assertEqual(dev.get_available_parents().count(), 4)
        self.assertIn(org, dev.get_available_parents().all())
        self.assertIn(arr, dev.get_available_parents().all())
        self.assertIn(mentor, dev.get_available_parents().all())
        self.assertIn(misc, dev.get_available_parents().all())
        self.assertNotIn(web, dev.get_available_parents().all())

        self.assertEqual(misc.get_available_parents().count(), 6)


class BoardPositionTestCase(TestCase):
    def test_str(self):
        holder = generate_member();

        board_position = BoardPosition(name="Testansvarlig", holder=holder)
        self.assertEqual(board_position.__str__(), "Testansvarlig")

    def test_holder(self):
        holder = generate_member()

        board_position = BoardPosition(name="Testansvarlig", holder=holder)
        self.assertEqual(holder, board_position.holder)

    def test_added_to_group(self):
        holder = generate_member()
        board_position = BoardPosition(name="Testansvarlig", holder=holder)
        board_position.save()

        group = Member.objects.filter(groups__name="Testansvarlig")
        self.assertEqual(holder in group, True)

    def test_added_to_board_group(self):
        holder = generate_member()
        board_position = BoardPosition(name="Testansvarlig", holder=holder)
        board_position.save()
        self.assertEqual(holder in board_position.user_set.all(), True)

    def test_new_holder(self):
        holder = generate_member()
        board_position = BoardPosition(name="Testansvarlig", holder=holder)
        board_position.save()

        new_holder = generate_member();
        board_position.holder = new_holder
        board_position.save()

        self.assertEqual(holder in board_position.user_set.all(), False);
        self.assertEqual(new_holder in board_position.user_set.all(), True);

        group = Member.objects.filter(groups__name="Testansvarlig")
        self.assertEqual(holder in group, False)
        self.assertEqual(new_holder in group, True)


class CommitteeTestCase(TestCase):
    def test_unique_leader_board(self):
        holder = generate_member()
        pos = BoardPosition.objects.create(name="Pos1", holder=holder)
        Committee.objects.create(name='Com1', leader_board=pos, email='com1@example.com')
        with self.assertRaises(ValidationError):
            Committee.objects.create(name='Com2', leader_board=pos, email='com1@example.com')

    def test_unique_leader_member(self):
        leader = generate_member()
        Committee.objects.create(name='Com1', leader_member=leader, email='com2@example.com')
        with self.assertRaises(ValidationError):
            Committee.objects.create(name='Com2', leader_member=leader, email='com2@example.com')

    def test_unique_email(self):
        email = 'com@example.com'
        leader1 = generate_member()
        leader2 = generate_member()
        Committee.objects.create(name='Com1', leader_member=leader1, email=email)
        with self.assertRaises(ValidationError):
            Committee.objects.create(name='Com2', leader_member=leader2, email=email)

    def test_unique_name(self):
        name = 'com'
        leader1 = generate_member()
        leader2 = generate_member()
        Committee.objects.create(name=name, leader_member=leader1, email='com1@example.com')
        with self.assertRaises(ValidationError):
            Committee.objects.create(name=name, leader_member=leader2, email='com2@example.com')

    def test_order(self):
        com3 = Committee.objects.create(name='com3', leader_member=generate_member(), email='com3@example.com', order=3)
        com1 = Committee.objects.create(name='com1', leader_member=generate_member(), email='com1@example.com', order=1)
        com4 = Committee.objects.create(name='com4', leader_member=generate_member(), email='com4@example.com', order=4)
        com2_1 = Committee.objects.create(name='com2_1', leader_member=generate_member(), email='com2_1@example.com', order=2)
        com0 = Committee.objects.create(name='com0', leader_member=generate_member(), email='com0@example.com')
        com2_2 = Committee.objects.create(name='com2_2', leader_member=generate_member(), email='com2_2@example.com', order=2)

        self.assertEqual(list(Committee.objects.all()), [com0, com1, com2_1, com2_2, com3, com4])

    def test_no_leader(self):
        with self.assertRaises(ValidationError):
            Committee.objects.create(name='com', email='com@example.com')

    def test_multiple_leaders(self):
        leader_member = generate_member()
        holder = generate_member()
        pos = BoardPosition.objects.create(name="Pos1", holder=holder)
        with self.assertRaises(ValidationError):
            Committee.objects.create(name='com', leader_member=leader_member, leader_board=pos, email='com@example.com')

    def test_leader(self):
        leader_member = generate_member()
        holder = generate_member()
        pos = BoardPosition.objects.create(name="Pos1", holder=holder)
        com = Committee.objects.create(name='com', leader_member=leader_member, email='com@example.com')
        self.assertEqual(com.leader, leader_member)

        com.leader_member = None
        com.leader_board = pos
        self.assertEqual(com.leader, holder)

    def test_change_from_boardPosition_to_leader(self):
        holder = generate_member()
        board_position = BoardPosition.objects.create(name="Testansvarlig", holder=holder)
        committee = Committee.objects.create(name="com", leader_board = board_position, email='com@example.com')
        new_leader = generate_member()
        committee.leader_member = new_leader
        committee.leader_board = None
        committee.save()
        self.assertEqual(committee.leader, new_leader)
        self.assertNotEqual(committee.leader, holder)


    def test_members(self):
        member1 = generate_member()
        member2 = generate_member()
        member3 = generate_member()
        holder = generate_member()
        pos = BoardPosition.objects.create(name="Pos1", holder=holder)
        com = Committee.objects.create(name='com', leader_board=pos, email='com@example.com')
        com.user_set.add(member1, member2, member3)

        self.assertEqual(set(com.user_set.all()), set([member1, member2, member3, holder]))
        self.assertEqual(set(com.members), set([member1, member2, member3]))
