from django.test import TestCase, Client
from django.contrib.auth.models import Permission
from django.urls import reverse

from ..models import Member, PercussionGroup

from .utils import generate_member


class PercussionGroupListTestCase(TestCase):
    def test_get_list(self):
        member1 = generate_member()
        member2 = generate_member()
        member3 = generate_member(first_name="Bob")
        member4 = generate_member()
        member4.is_active = False
        member4.save()
        percussion_group = PercussionGroup.objects.create()
        member2.percussion_group = percussion_group
        member2.save()
        self.client = Client()
        self.client.force_login(member1)

        response = self.client.get(reverse('percussion_group_list'))
        self.assertTrue(percussion_group in response.context['groups'])
        self.assertEqual(list(response.context['unassigned']), [member3, member1])


class DeletePercussionGroupTestCase(TestCase):
    def test_delete(self):
        member = generate_member()
        member.user_permissions.add(
            Permission.objects.get(codename="change_percussion_group"))
        self.client.force_login(member)
        percussion_group = PercussionGroup.objects.create()
        self.assertEqual(len(PercussionGroup.objects.all()), 1)
        response = self.client.get(reverse("percussion_group_delete", args=[percussion_group.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(PercussionGroup.objects.all()), 0)


class AddPercussionGroupTestCase(TestCase):
    def test_delete(self):
        member = generate_member()
        member.user_permissions.add(
            Permission.objects.get(codename="change_percussion_group"))
        self.client.force_login(member)
        response = self.client.get(reverse("percussion_group_add"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(PercussionGroup.objects.all()), 1)


class ChangePercussionGroupTestCase(TestCase):
    def setUp(self):
        self.member = generate_member()
        self.member.user_permissions.add(
            Permission.objects.get(codename="change_percussion_group"))
        self.client.force_login(self.member)

    def test_context(self):
        member1 = generate_member()
        member2 = generate_member()
        member3 = generate_member()
        percussion_group1 = PercussionGroup.objects.create()
        member1.percussion_group = percussion_group1
        member1.save()
        percussion_group2 = PercussionGroup.objects.create()
        member2.percussion_group = percussion_group2
        member2.save()

        response = self.client.get(reverse("percussion_group_change", args=[percussion_group1.pk]))
        self.assertTrue(percussion_group2 in response.context['other_groups'])
        self.assertTrue(percussion_group1 not in response.context['other_groups'])
        self.assertTrue(member3 in response.context['unassigned'])
        self.assertTrue(member2 not in response.context['unassigned'])
        self.assertTrue(member1 not in response.context['unassigned'])

    def test_add_member_via_post(self):
        member1 = generate_member()
        member2 = generate_member()
        member3 = generate_member()
        percussion_group = PercussionGroup.objects.create()

        post_data = {'leader': [str(member1.pk)], 'members[]': [str(member2.pk), str(member1.pk)]}
        self.client.post(reverse("percussion_group_change", args=[percussion_group.pk]), post_data)
        percussion_group_members = Member.objects.filter(percussion_group=percussion_group)
        self.assertTrue(member1 in percussion_group_members)
        self.assertTrue(member2 in percussion_group_members)
        self.assertTrue(member3 not in percussion_group_members)

    def test_remove_member_and_change_leader_via_post(self):
        member1 = generate_member()
        member2 = generate_member()
        percussion_group = PercussionGroup.objects.create()

        member2.percussion_group = percussion_group
        member2.save()

        # This post should remove member1 and set member2 as leader
        post_data = {'leader': [str(member2.pk)], 'members[]': [str(member2.pk)]}
        self.client.post(reverse("percussion_group_change", args=[percussion_group.pk]), post_data)
        percussion_group_members = Member.objects.filter(percussion_group=percussion_group)
        self.assertTrue(member1 not in percussion_group_members)
        self.assertTrue(member2 in percussion_group_members)

    def test_illegal_post_data(self):
        member1 = generate_member()
        member2 = generate_member()
        percussion_group = PercussionGroup.objects.create()

        post_data = {'members[]': [str(member2.pk)]}  # should also contain leader
        response = self.client.post(reverse("percussion_group_change", args=[percussion_group.pk]), post_data)
        self.assertEqual(response.status_code, 404)

        post_data = {'leader': [str(member1.pk)]}  # should also contain members[]
        self.client.post(reverse("percussion_group_change", args=[percussion_group.pk]), post_data)
        self.assertEqual(response.status_code, 404)
