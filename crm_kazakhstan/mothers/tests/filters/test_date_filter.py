from datetime import datetime
from freezegun import freeze_time

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.db import models
from django.contrib import admin

from mothers.filters import DateFilter
from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

Mother: models
Stage: models

User = get_user_model()


class DateFilterTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.factory = RequestFactory()
        self.mother_admin = MotherAdmin(Mother, admin.site)

    def test_today_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        mother = Mother.objects.create(name="Today")
        mother.date_create = timezone.now()
        mother.save()
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = DateFilter(request=request, params={'date_filter': 'today'}, model=Mother, model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Today')

    def test_yesterday_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        mother = Mother.objects.create(name="Yesterday")
        mother.date_create = timezone.now() - timezone.timedelta(days=1)
        mother.save()
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = DateFilter(request=request, params={'date_filter': 'yesterday'}, model=Mother,
                       model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Yesterday')

    @freeze_time("2023-12-12 20:30:00")
    def test_past_7_days_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        with freeze_time("2023-12-05 16:30:00"):
            mother = Mother.objects.create(name="Past 7 days")

            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = DateFilter(request=request, params={'date_filter': 'past_7_days'}, model=Mother,
                       model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Past 7 days')

    @freeze_time("2023-12-12 20:30:00")
    def test_past_7_days_filter_middle_of_week(self):
        request = self.factory.get('/')
        request.user = self.superuser

        with freeze_time("2023-12-05 16:30:00"):
            mother = Mother.objects.create(name="Past 7 days")

            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = DateFilter(request=request, params={'date_filter': 'past_7_days'}, model=Mother,
                       model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Past 7 days')

    @freeze_time("2023-12-12 20:30:00")
    def test_past_7_days_filter_middle_of_week(self):
        request = self.factory.get('/')
        request.user = self.superuser

        with freeze_time("2023-12-10 16:30:00"):
            mother = Mother.objects.create(name="Past 7 days second")

            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = DateFilter(request=request, params={'date_filter': 'past_7_days'}, model=Mother,
                       model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Past 7 days second')

    @freeze_time("2023-12-24 20:30:00")
    def test_past_14_days_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        with freeze_time("2023-12-10 16:30:00"):
            mother = Mother.objects.create(name="Past 14 days")

            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = DateFilter(request=request, params={'date_filter': 'past_14_days'}, model=Mother,
                       model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Past 14 days')

    @freeze_time("2023-12-24 20:30:00")
    def test_past_14_days_filter_middle_of_two_weeks(self):
        request = self.factory.get('/')
        request.user = self.superuser

        with freeze_time("2023-12-15 16:30:00"):
            mother = Mother.objects.create(name="Past 14 days second")

            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = DateFilter(request=request, params={'date_filter': 'past_14_days'}, model=Mother,
                       model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Past 14 days second')

    @freeze_time("2023-12-24 20:30:00")
    def test_current_month_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        mother = Mother.objects.create(name="Start of the Month")
        mother.date_create = datetime(2023, 12, 11, 20, 20, 0, tzinfo=timezone.utc)
        mother.save()
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = DateFilter(request=request, params={'date_filter': 'current_month'}, model=Mother,
                       model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        self.assertEqual(queryset.first().name, 'Start of the Month')

    @freeze_time("2023-12-24 20:30:00")
    def test_not_current_month_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser

        mother = Mother.objects.create(name="Start of the Month second")
        mother.date_create = datetime(2023, 11, 11, 20, 20, 0, tzinfo=timezone.utc)
        mother.save()
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        f = DateFilter(request=request, params={'date_filter': 'current_month'}, model=Mother,
                       model_admin=self.mother_admin)
        queryset = f.queryset(request=request, queryset=self.mother_admin.get_queryset(request))

        with self.assertRaises(AttributeError):
            self.assertEqual(queryset.first().name, "Start of the Month second")
