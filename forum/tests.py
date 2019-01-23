from datetime import date

from django.test import TestCase, Client
from django.contrib.auth.models import Permission

from .models import Post
from members.models import Member, InstrumentGroup, BoardPosition
from django.urls import reverse

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


class PostTestCase(TestCase):
    def setUp(self):
        test_member['instrument'] = InstrumentGroup.objects.create(name='Testolin')

    def test_forum_choices(self):
        """Check that the forum constants haven't changed.

        If you need to change the forum constants (Post.VARIOUS etc.)
        you must also change every post in that forum to point to that
        new constant.

        If you don't do this all posts that have been posted in that forum
        will be unavailable.
        """
        self.assertEqual(Post.MUSIC, 'musikk')
        self.assertEqual(Post.VARIOUS, 'diverse')
        self.assertEqual(Post.BOARD, 'styret')

    def test_forum_access(self):
        member = Member.objects.create_user(**test_member)

        self.assertTrue(Post.user_can_access_forum(member, Post.MUSIC))
        self.assertTrue(Post.user_can_access_forum(member, Post.VARIOUS))
        self.assertFalse(Post.user_can_access_forum(member, Post.BOARD))

        position = BoardPosition()
        position.holder = member
        position.title = 'Tester'
        position.email = 'test@testing.com'
        position.save()
        position.permissions.add(
            Permission.objects.get(codename='view_board_forum')
        )

        # Load member again to get the new permission
        member = Member.objects.get(email=test_member['email'])

        self.assertTrue(Post.user_can_access_forum(member, Post.MUSIC))
        self.assertTrue(Post.user_can_access_forum(member, Post.VARIOUS))
        self.assertTrue(Post.user_can_access_forum(member, Post.BOARD))


class PostDetailTestCase(TestCase):
    def setUp(self):
        test_member['instrument'] = InstrumentGroup.objects.create(name='Testolin')

    def test_get_context_data(self):
        self.client = Client()
        member = Member.objects.create_user(**test_member)
        self.client.force_login(member)
        forum_post = Post.objects.create(title='testpost')

        response = self.client.get(forum_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('forum_post_list', args=[forum_post.forum]))

        response = self.client.get(forum_post.get_absolute_url() + '?prev=all_forum_post_list')
        self.assertContains(response, reverse('all_forum_post_list'))
        self.assertNotContains(response, "'" + reverse('forum_post_list', args=[forum_post.forum]) + "'")
        # the quotes are added because this link is the start of anoter link


class PostListTestCase(TestCase):
    def setUp(self):
        test_member['instrument'] = InstrumentGroup.objects.create(name='Testolin')
        self.client = Client()
        self.member = Member.objects.create_user(**test_member)
        self.client.force_login(self.member)
        self.forum_post = Post.objects.create(title='testpost')

    def test_post_list(self):
        response = self.client.get(reverse('forum_post_list', args=['diverse']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testpost')
        response = self.client.get(reverse('forum_post_list', args=['musikk']))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'testpost')
        response = self.client.get(reverse('forum_post_list', args=['what_not']))
        self.assertEqual(response.status_code, 404)

    def test_all_post_list(self):
        response = self.client.get(reverse('all_forum_post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testpost')
