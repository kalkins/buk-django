from datetime import timedelta

from django.test import TestCase, Client
from django.utils import timezone
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from members.models import Instrument
from members.tests import generate_member

from .models import Poll, PollOption
from .forms import PollAnswerForm


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
        with self.assertRaisesMessage(IntegrityError, 'poll_id'):
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


class PollAnswerFormTestCase(TestCase):
    def setUp(self):
        self.member1 = generate_member()
        self.member2 = generate_member()
        self.poll1 = Poll.objects.create(title='Poll 1')
        self.poll2 = Poll.objects.create(title='Poll 1')
        self.option1 = PollOption.objects.create(title='Option 1', poll=self.poll1)
        self.option2 = PollOption.objects.create(title='Option 2', poll=self.poll1)
        self.option3 = PollOption.objects.create(title='Option 3', poll=self.poll2)
        self.option4 = PollOption.objects.create(title='Option 4', poll=self.poll2)

    def test_queryset(self):
        form1 = PollAnswerForm(poll=self.poll1, member=self.member1)
        form2 = PollAnswerForm(poll=self.poll2, member=self.member1)

        self.assertEqual(list(form1.fields['options'].queryset.all()), [self.option1, self.option2])
        self.assertEqual(list(form2.fields['options'].queryset.all()), [self.option3, self.option4])

    def test_create_without_poll(self):
        with self.assertRaisesMessage(ValueError, 'poll'):
            PollAnswerForm(member=self.member1)

    def test_create_without_member(self):
        with self.assertRaisesMessage(ValueError, 'member'):
            PollAnswerForm(poll=self.poll1)

    def test_deadline(self):
        form = PollAnswerForm(poll=self.poll1, member=self.member1)
        self.assertFalse(form.fields['options'].disabled)

        self.poll1.deadline = timezone.now() - timedelta(minutes=5)
        self.poll1.save()
        form = PollAnswerForm(poll=self.poll1, member=self.member1)
        self.assertTrue(form.fields['options'].disabled)

    def test_initial(self):
        form = PollAnswerForm(poll=self.poll1, member=self.member1)
        self.assertIsNone(form.fields['options'].initial)

        self.option1.members.add(self.member1)
        form = PollAnswerForm(poll=self.poll1, member=self.member1)
        self.assertEqual(form.fields['options'].initial, self.option1)

    def test_save(self):
        form = PollAnswerForm(
            poll=self.poll1,
            member=self.member1,
            data={
                'options': self.option1.pk,
            }
        )
        form.save()
        self.assertIn(self.member1, PollOption.objects.get(pk=self.option1.pk).members.all())

        form = PollAnswerForm(
            poll=self.poll2,
            member=self.member2,
            data={}
        )
        with self.assertRaisesMessage(ValueError, 'Data doesn\'t validate'):
            form.save()

    def test_validation(self):
        form = PollAnswerForm(
            poll=self.poll1,
            member=self.member1,
            data={
                'options': self.option1.pk,
            }
        )
        self.assertNotIn('options', form.errors)

        form = PollAnswerForm(
            poll=self.poll1,
            member=self.member1,
            data={}
        )
        self.assertIn('options', form.errors)

        form = PollAnswerForm(
            poll=self.poll1,
            member=self.member1,
            data={
                'options': None,
            }
        )
        self.assertIn('options', form.errors)

        self.poll1.deadline = timezone.now() + timedelta(minutes=5)
        form = PollAnswerForm(
            poll=self.poll1,
            member=self.member1,
            data={
                'options': self.option1.pk,
            }
        )
        self.assertNotIn('options', form.errors)

        self.poll2.deadline = timezone.now() - timedelta(minutes=5)
        form = PollAnswerForm(
            poll=self.poll2,
            member=self.member2,
            data={
                'options': self.option3.pk,
            }
        )
        self.assertIn('options', form.errors)

        form = PollAnswerForm(
            poll=self.poll1,
            member=self.member1,
            data={
                'options': self.option3.pk,
            }
        )
        self.assertIn('options', form.errors)
