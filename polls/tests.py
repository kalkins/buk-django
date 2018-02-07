from datetime import timedelta

from django.test import TestCase, Client
from django.utils import timezone

from .models import Poll


class PollTestCase(TestCase):
    def test_create_without_deadline(self):
        title = 'Test poll'
        poll = Poll.objects.create(title=title)

        self.assertEqual(poll.title, title)
        self.assertEqual(str(poll), title)
        self.assertIsNone(poll.deadline)
        self.assertFalse(poll.is_past_deadline)

    def test_create_with_deadline(self):
        title = 'Test poll'
        future = timezone.now() + timedelta(minutes=5)
        past = timezone.now() - timedelta(minutes=5)
        poll = Poll.objects.create(title=title, deadline=future)

        self.assertEqual(poll.title, title)
        self.assertEqual(str(poll), title)
        self.assertEqual(poll.deadline, future)
        self.assertFalse(poll.is_past_deadline)

        poll.deadline = past
        poll.save()

        self.assertEqual(poll.deadline, past)
        self.assertTrue(poll.is_past_deadline)

    def test_url(self):
        title = 'Test poll'
        poll = Poll.objects.create(title=title)
        c = Client()
        response = c.get(poll.get_absolute_url())

        self.assertIn(response.status_code, [200, 302])
