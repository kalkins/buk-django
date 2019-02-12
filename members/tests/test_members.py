from datetime import date
import datetime

from django.test import TestCase, Client
from django.forms import modelform_factory
from django.core.management import call_command
from django.utils.six import StringIO
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from utils.forms import formset_to_post, form_to_post

from ..models import Member, PercussionGroup, BoardPosition, InheritanceGroup, MembershipPeriod
from ..forms import MemberAddForm, MembershipPeriodFormset, LeavePeriodFormset
from base.tests import permission_to_perm
from .utils import generate_member, generate_member_attrs


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
        holder = generate_member()

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

        new_holder = generate_member()
        board_position.holder = new_holder
        board_position.save()

        self.assertEqual(holder in board_position.user_set.all(), False)
        self.assertEqual(new_holder in board_position.user_set.all(), True)

        group = Member.objects.filter(groups__name="Testansvarlig")
        self.assertEqual(holder in group, False)
        self.assertEqual(new_holder in group, True)


class MemberListTestCase(TestCase):
    def setUp(self):
        self.member1 = generate_member(first_name="aadne")
        self.member2 = generate_member(first_name="abalo")
        self.member2.is_active = False
        self.member2.save()
        self.member3 = generate_member(first_name="abba")
        self.client = Client()
        self.client.force_login(self.member1)

    def test_get_all_members(self):
        response = self.client.get(reverse("member_list_all"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["show_all"], True)
        self.assertEqual(
            set(response.context["members"]),
            set([self.member1, self.member2, self.member3]))

    def test_get_active_members(self):
        response = self.client.get(reverse("member_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["show_all"], False)
        self.assertEqual(
            set(response.context["members"]),
            set([self.member1, self.member3]))


class MemberAddFormTestCase(TestCase):
    def test_memberShipPeriod_added(self):
        member_attributes = generate_member_attrs()
        today = date.today()
        member_attributes['joined_date'] = today
        member_attributes['instrument'] = member_attributes['instrument'].pk
        form = MemberAddForm(data=member_attributes)
        if form.is_valid():
            form.save()
        else:
            self.fail("form not valid " + form.errors)
        self.assertEqual(
            MembershipPeriod.objects.get(member=form.instance).start, today)


class ChangeMemberTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_change_self(self):
        member = generate_member()
        self.client.force_login(member)
        response = self.client.get(reverse("member_change", args=[member.pk]))
        self.assertEqual(response.status_code, 200)

    def test_change_other_member_with_permission(self):
        member = generate_member()
        member.user_permissions.add(
            Permission.objects.get(codename="change_member"))
        other_member = generate_member()
        self.client.force_login(member)
        response = self.client.get(
            reverse("member_change", args=[other_member.pk]))
        self.assertEqual(response.status_code, 200)

    def test_change_without_permission(self):
        member = generate_member()
        other_member = generate_member()
        self.client.force_login(member)
        response = self.client.get(
            reverse("member_change", args=[other_member.pk]))
        self.assertEqual(response.status_code, 403)

    def test_percussion_group_in_form(self):
        member = generate_member()
        self.client.force_login(member)
        first_response = self.client.get(
            reverse("member_change", args=[member.pk]))
        self.assertFalse(
            "percussion_group" in first_response.context["form"].fields)

        member.user_permissions.add(
            Permission.objects.get(codename="change_percussion_group"))
        second_response = self.client.get(
            reverse("member_change", args=[member.pk]))
        self.assertTrue(
            "percussion_group" in second_response.context["form"].fields)

    def test_get_context_data_on_get(self):
        member = generate_member()
        self.client.force_login(member)
        response = self.client.get(reverse("member_change", args=[member.pk]))
        self.assertTrue('membership_period_formset' in response.context.keys())
        self.assertTrue('leave_period_formset' in response.context.keys())

    def test_valid_form(self):
        now = timezone.now().date()
        year_from_now = now + datetime.timedelta(days=365)
        membership_period_formset = MembershipPeriodFormset(initial=[
            {"start": now,
             "end": year_from_now}
        ])
        leave_period_formset = LeavePeriodFormset(initial=[
            {"start": year_from_now,
             "end": now}
        ])  # There's an error here

        member = generate_member()
        fields = ['email', 'first_name', 'last_name', 'instrument', 'phone',
                  'birthday', 'address', 'zip_code', 'city', 'origin', 'occupation',
                  'has_car', 'has_towbar', 'musical_background', 'about_me']
        formclass = modelform_factory(Member, fields=fields)
        member_form = formclass(instance=member)
        member_form_data = form_to_post(member_form)

        post_data = {**formset_to_post(membership_period_formset), **formset_to_post(leave_period_formset), **member_form_data}

        self.client.force_login(member)
        response = self.client.post(reverse("member_change", args=[member.pk]), post_data)
        self.assertEqual(response.status_code, 200)  # form is not valid

        leave_period_formset = LeavePeriodFormset(initial=[
            {"start": now,
             "end": year_from_now}
        ])  # Error is fixed

        post_data = {**formset_to_post(membership_period_formset), **formset_to_post(leave_period_formset), **member_form_data}

        response = self.client.post(reverse("member_change", args=[member.pk]), post_data)
        self.assertEqual(response.status_code, 302)  # form is valid and user is redirected
