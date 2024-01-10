from datetime import datetime, time
from freezegun import freeze_time

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import Condition, Mother
from mothers.admin import MotherAdmin
from mothers.filters import ConditionListFilter

MotherAdmin: admin.ModelAdmin
Condition: models
Mother: models
Planned: models
User = get_user_model()


class ConditionListFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create_user(username='staffuser', password='staffuserpassword', is_staff=True)

        self.factory = RequestFactory()

        self.admin_site = AdminSite()
        self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)

    @freeze_time("2023-12-12")
    def test_when_Condition_scheduled_date_less_date_today_and_finished_False(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)

    @freeze_time("2023-12-12")
    def test_when_Condition_scheduled_date_equal_date_today_and_finished_False(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)

    @freeze_time("2023-12-12")
    def test_when_Condition_scheduled_date_bigger_date_today_and_finished_False(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 13, tzinfo=timezone.utc),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12")
    def test_when_Condition_scheduled_date_less_date_today_and_finished_True(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            condition='FR3',
            finished=True
        )
        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12")
    def test_when_Condition_scheduled_date_equal_date_today_and_finished_True(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            condition='FR3',
            finished=True
        )
        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12")
    def test_when_Condition_scheduled_date_bigger_date_today_and_finished_True(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 13, tzinfo=timezone.utc),
            condition='FR3',
            finished=True
        )
        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12")
    def test_when_Condition_scheduled_date_less_date_today_and_scheduled_time_and_finished_False(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12")
    def test_when_Condition_scheduled_date_less_date_today_and_scheduled_time_and_finished_True(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            condition='FR3',
            finished=True
        )
        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12 20:30:00")
    def test_when_Condition_scheduled_date_equal_date_today_and_scheduled_time_less_datetime_and_finished_False(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            condition='FR3',
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)

    @freeze_time("2023-12-12 20:30:00")
    def test_when_Condition_scheduled_date_equal_date_today_and_scheduled_time_equal_datetime_and_finished_False(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(20, 30, 0),
            condition='FR3',
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)

    @freeze_time("2023-12-12 20:30:00")
    def test_when_Condition_scheduled_date_equal_date_today_and_scheduled_time_bigger_datetime_and_finished_False(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12 20:30:00")
    def test_when_Condition_scheduled_date_bigger_date_today_and_scheduled_time_and_finished_False(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 13, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12 20:30:00")
    def test_when_Condition_scheduled_date_equal_date_today_and_scheduled_time_less_datetime_and_finished_True(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            condition='FR3',
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12 20:30:00")
    def test_when_Condition_scheduled_date_equal_date_today_and_scheduled_time_equal_datetime_and_finished_True(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(20, 30, 0),
            condition='FR3',
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12 20:30:00")
    def test_when_Condition_scheduled_date_equal_date_today_and_scheduled_time_bigger_datetime_and_finished_True(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12 20:30:00")
    def test_when_Condition_scheduled_date_bigger_date_today_and_scheduled_time_and_finished_True(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 13, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    @freeze_time("2023-12-12 20:30:00")
    def test_Condition_scheduled_date_not_in_datetime_list_when_previous_finished_conditions_exists_with_scheduled_time(
            self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(20, 20, 0),
            condition='FR3',
            finished=True
        )
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            condition='FR3',
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)
