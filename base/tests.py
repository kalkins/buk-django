from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Period
import datetime


class BasePeriodFormsetTestCase(TestCase):
    def test_end_before_start(self):
        now = timezone.now()
        year_ago = timezone.now() - datetime.timedelta(days=365)
        with self.assertRaises(ValidationError):
            period = Period(start=now, end=year_ago)
            period.clean()

    def test_contains(self):
        now = timezone.now()
        year_ago = timezone.now() - datetime.timedelta(days=365)
        half_year_ago = timezone.now() - datetime.timedelta(days=182)
        two_days_ago = timezone.now() - datetime.timedelta(days=2)
        half_year = timezone.now() + datetime.timedelta(days=182)
        period = Period(start=half_year_ago)
        self.assertTrue(period.contains(half_year_ago))
        self.assertTrue(period.contains(now))
        self.assertFalse(period.contains(year_ago))
        period.end = now
        self.assertTrue(period.contains(two_days_ago))
        self.assertFalse(period.contains(year_ago))
        self.assertFalse(period.contains(half_year))

    def test_str(self):
        now = timezone.now()
        year_ago = timezone.now() - datetime.timedelta(days=365)
        period = Period(start=year_ago)
        period.end = now
        self.assertTrue(year_ago.__str__() in period.__str__())
        self.assertTrue(now.__str__() in period.__str__())
