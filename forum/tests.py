from datetime import date

from django.test import TestCase
from django.contrib.auth.models import Permission

from .models import Post
from members.models import Member, Instrument, BoardPosition

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
        test_member['instrument'] = Instrument.objects.create(name='Testolin')

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
