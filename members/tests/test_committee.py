from django.test import TestCase
from django.contrib.auth.models import Permission
from django.urls import reverse

from ..models import Member, Committee
from ..forms import CommitteeChangeForm, CommitteeMembershipFormset

from base.tests import management_form_to_post
from .utils import generate_member


class ChangeCommitteeTestCase(TestCase):
    def setUp(self):
        self.member = generate_member()
        self.member.user_permissions.add(
            Permission.objects.get(codename="change_committee"))
        self.client.force_login(self.member)

    def test_permission(self):
        member = generate_member()
        self.client.force_login(member)
        committee = Committee.objects.create(name='Com1', leader=member, email='com1@example.com')
        response = self.client.get(reverse("change_committee", args=[committee.pk]))
        self.assertEqual(response.status_code, 403)

        member.user_permissions.add(
            Permission.objects.get(codename="change_committee"))
        member.save()
        response = self.client.get(reverse("change_committee", args=[committee.pk]))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        member1 = generate_member()
        committee = Committee.objects.create(name='Com1', leader=member1, email='com1@example.com')
        response = self.client.get(reverse("change_committee", args=[committee.pk]))
        self.assertIn('committee_form', response.context)
        self.assertIn('formset', response.context)


class CommitteeChangeFormTestCase(TestCase):
    def form_data(self, committee):
        return {
            'name': committee.name,
            'description': committee.description,
            'email': committee.email,
            'order': str(committee.order),
            'leader': str(committee.leader.pk),
            'leader_title': committee.leader_title,
        }

    def test_change_leader(self):
        member1 = generate_member(first_name='member1')
        member2 = generate_member(first_name='member2')
        committee = Committee.objects.create(name='Com1', leader=member1, email='com1@example.com')

        data = {
            **self.form_data(committee),
            'leader': str(member2.pk),
        }
        form = CommitteeChangeForm(data, instance=committee)
        self.assertTrue(form.is_valid(), msg=form.errors)
        form.save()

        committee_members = Member.objects.filter(groups__pk=committee.pk)
        committee = Committee.objects.get(pk=committee.pk)

        self.assertEqual(member2, committee.leader)
        self.assertNotIn(member1, committee.members.all())
        self.assertNotIn(member1, committee_members)
        self.assertNotIn(member2, committee.members.all())
        self.assertIn(member2, committee_members)


class CommitteeMembershipFormsetTestCase(TestCase):
    prefix = CommitteeMembershipFormset().prefix

    def formset_post(self, committee=None):
        formset = CommitteeMembershipFormset(instance=committee)
        data = management_form_to_post(formset.management_form)

        for i, _ in enumerate(formset.forms):
            data[f'{self.prefix}-{i}-member'] = ''
            data[f'{self.prefix}-{i}-title'] = 'Medlem'
            data[f'{self.prefix}-{i}-DELETE'] = ''
            pass

        return data

    def membership(self, committee, member):
        model = committee.members.through
        return model.objects.get(committee=committee, member=member)

    def test_add_member(self):
        member1 = generate_member()
        member2 = generate_member()
        committee = Committee.objects.create(name='Com1', leader=member1, email='com1@example.com')

        data = {
            **self.formset_post(committee),
            f'{self.prefix}-0-member': str(member2.pk),
        }
        formset = CommitteeMembershipFormset(data, instance=committee)
        self.assertTrue(formset.is_valid(), msg=formset.errors)
        formset.save()

        committee_members = Member.objects.filter(groups__pk=committee.pk)
        self.assertIn(member2, committee_members)
        self.assertIn(member2, committee.members.all())

    def test_remove_member(self):
        member1 = generate_member(first_name='member1')
        member2 = generate_member(first_name='member2')
        committee = Committee.objects.create(name='Com1', leader=member1, email='com1@example.com')
        committee.add_member(member2)

        data = {
            **self.formset_post(committee),
            f'{self.prefix}-0-id': self.membership(committee, member2).pk,
            f'{self.prefix}-0-member': str(member2.pk),
            f'{self.prefix}-0-DELETE': 'on',
        }
        formset = CommitteeMembershipFormset(data, instance=committee)
        self.assertTrue(formset.is_valid(), msg=formset.errors)
        formset.save()

        committee_members = Member.objects.filter(groups__pk=committee.pk)
        committee = Committee.objects.get(pk=committee.pk)
        self.assertNotIn(member2, committee.members.all())
        self.assertNotIn(member2, committee_members)

    def test_change_member(self):
        member1 = generate_member(first_name='member1')
        member2 = generate_member(first_name='member2')
        member3 = generate_member(first_name='member3')
        committee = Committee.objects.create(name='Com1', leader=member1, email='com1@example.com')
        committee.add_member(member2)

        data = {
            **self.formset_post(committee),
            f'{self.prefix}-0-id': self.membership(committee, member2).pk,
            f'{self.prefix}-0-member': str(member3.pk),
        }
        formset = CommitteeMembershipFormset(data, instance=committee)
        self.assertTrue(formset.is_valid(), msg=formset.errors)
        formset.save()

        committee_members = Member.objects.filter(groups__pk=committee.pk)
        committee = Committee.objects.get(pk=committee.pk)
        self.assertNotIn(member2, committee.members.all())
        self.assertNotIn(member2, committee_members)
        self.assertIn(member3, committee.members.all())
        self.assertIn(member3, committee_members)
