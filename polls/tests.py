from datetime import timedelta

from django.test import TestCase, Client
from django.utils import timezone
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from members.models import Instrument
from members.tests import generate_member

from .models import Poll, PollOption


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


class PollOptionTestCase(TestCase):
    def setUp(self):
        self.poll = Poll.objects.create(title='Poll title')

    def test_create(self):
        title = 'Option title'
        option = PollOption.objects.create(poll=self.poll, title=title)

        self.assertEqual(option.title, title)
        self.assertEqual(str(option), title)

    def test_create_without_poll(self):
        title = 'Option title'
        with self.assertRaisesMessage(IntegrityError, 'NOT NULL constraint failed'):
            PollOption.objects.create(title=title)

    def test_instruments(self):
        instrument1 = Instrument.objects.create(name='Inst1')
        instrument2 = Instrument.objects.create(name='Inst2')

        member1 = generate_member(instrument=instrument1)
        member2 = generate_member(instrument=instrument1)
        member3 = generate_member(instrument=instrument2)

        option = PollOption.objects.create(poll=self.poll, title='Option 1')
        option.members.add(member1)
        option.members.add(member2)
        option.members.add(member3)

        for inst in option.instruments():
            if inst['name'] == instrument1.name:
                self.assertEqual(inst['count'], 2)
            elif inst['name'] == instrument2.name:
                self.assertEqual(inst['count'], 1)

    def test_delete_poll(self):
        member = generate_member()
        option = PollOption.objects.create(poll=self.poll, title='Option 1')
        option.members.add(member)
        self.poll.delete()

        with self.assertRaisesMessage(ObjectDoesNotExist, 'matching query does not exist'):
            PollOption.objects.get(pk=option.pk)
