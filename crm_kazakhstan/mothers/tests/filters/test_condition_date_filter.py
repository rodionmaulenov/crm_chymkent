from datetime import date, time, datetime
from freezegun import freeze_time

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.db import models
from django.contrib import admin

from mothers.filters import ConditionDateFilter
from mothers.models import Mother, Stage, Condition
from mothers.admin import MotherAdmin

Mother: models
Condition: models
Stage: models

User = get_user_model()


class ConditionDateFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.factory = RequestFactory()
        self.mother_admin = MotherAdmin(Mother, admin.site)

    def test_today_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        mother = Mother.objects.create(name="Today")
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        condition = Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2023, 12, 10),
                                             scheduled_time=time(18, 20, 0), reason='some reason')
        condition.created = timezone.now()
        condition.save()

        f = ConditionDateFilter(request=request, params={'date_filter': 'today'}, model=Mother,
                                model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Today')

    @freeze_time("2023-12-12 20:30:00")
    def test_past_7_days_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        with freeze_time("2023-12-05 16:30:00"):
            mother = Mother.objects.create(name="Past 7 days")
            Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2023, 12, 5),
                                     scheduled_time=time(16, 30, 0), reason='some reason')

            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = ConditionDateFilter(request=request, params={'date_filter': 'past_7_days'}, model=Mother,
                                model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Past 7 days')

    @freeze_time("2023-12-12 20:30:00")
    def test_past_7_days_filter_middle_of_week(self):
        request = self.factory.get('/')
        request.user = self.superuser

        with freeze_time("2023-12-05 16:30:00"):
            mother = Mother.objects.create(name="Past 7 days")
            Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2023, 12, 5),
                                     scheduled_time=time(16, 30, 0), reason='some reason')

            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = ConditionDateFilter(request=request, params={'date_filter': 'past_7_days'}, model=Mother,
                                model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Past 7 days')

    @freeze_time("2023-12-24 20:30:00")
    def test_past_14_days_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        with freeze_time("2023-12-10 16:30:00"):
            mother = Mother.objects.create(name="Past 14 days")
            Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2023, 12, 10),
                                     scheduled_time=time(16, 30, 0), reason='some reason')

            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = ConditionDateFilter(request=request, params={'date_filter': 'past_14_days'}, model=Mother,
                                model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Past 14 days')

    @freeze_time("2023-12-24 20:30:00")
    def test_past_14_days_filter_middle_of_two_weeks(self):
        request = self.factory.get('/')
        request.user = self.superuser

        with freeze_time("2023-12-15 16:30:00"):
            mother = Mother.objects.create(name="Past 14 days second")
            Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2023, 12, 10),
                                     scheduled_time=time(16, 30, 0), reason='some reason')

            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = ConditionDateFilter(request=request, params={'date_filter': 'past_14_days'}, model=Mother,
                                model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Past 14 days second')

    @freeze_time("2023-12-24 20:30:00")
    def test_current_month_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        mother = Mother.objects.create(name="Start of the Month")
        condition = Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2023, 12, 10),
                                             scheduled_time=time(16, 30, 0), reason='some reason')
        condition.created = datetime(2023, 12, 11, 20, 20, 0, tzinfo=timezone.utc)
        condition.save()

        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = ConditionDateFilter(request=request, params={'date_filter': 'current_month'}, model=Mother,
                                model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Start of the Month')

    @freeze_time("2023-12-24 20:30:00")
    def test_not_current_month_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        mother = Mother.objects.create(name="Start of the Month second")
        condition = Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2023, 12, 10),
                                             scheduled_time=time(16, 30, 0), reason='some reason')
        condition.created = datetime(2023, 11, 11, 20, 20, 0, tzinfo=timezone.utc)
        condition.save()
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = ConditionDateFilter(request=request, params={'date_filter': 'current_month'}, model=Mother,
                                model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        with self.assertRaises(AttributeError):
            self.assertEqual(queryset.first().name, "Start of the Month second")
