from datetime import datetime, time
from freezegun import freeze_time

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone
from guardian.shortcuts import assign_perm

from mothers.models import Condition, Mother, Stage
from mothers.admin import MotherAdmin
from mothers.filters import AuthConditionListFilter

MotherAdmin: admin.ModelAdmin
Condition: models
Mother: models
Stage: models
User = get_user_model()


class AuthConditionListFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create_user(username='staffuser', password='staffuserpassword', is_staff=True)
        self.rushana = User.objects.create_user(username='Rushana', password='password')

        self.factory = RequestFactory()

        self.admin_site = AdminSite()
        self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)

    @freeze_time("2023-12-12")
    def test_superuser_by_date(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = AuthConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertTrue(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(len(queryset), 1)

    @freeze_time("2023-12-12")
    def test_superuser_by_date_and_time(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.superuser
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = AuthConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )

        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertTrue(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(len(queryset), 1)

    @freeze_time("2023-12-12")
    def test_staff_has_not_permissions_user_by_date(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.staff_user
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = AuthConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertFalse(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(queryset, None)

    @freeze_time("2023-12-12")
    def test_rushana_has_not_permissions_user_by_date(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.rushana
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = AuthConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertFalse(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(queryset, None)

    @freeze_time("2023-12-12")
    def test_staff_user_has_not_permissions_by_date_and_time(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.staff_user
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = AuthConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )

        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertFalse(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(queryset, None)

    @freeze_time("2023-12-12")
    def test_rushana_has_not_permissions_by_date_and_time(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.rushana
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = AuthConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )

        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertFalse(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(queryset, None)

    @freeze_time("2023-12-12")
    def test_rushana_has_permissions_user_by_date(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            condition='FR3',
            finished=False
        )
        assign_perm('view_mother', self.rushana, mother)
        assign_perm('change_mother', self.rushana, mother)

        request = self.factory.get('/')
        request.user = self.rushana
        request.GET = {'date_or_time': 'by_date'}

        filter_instance = AuthConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertTrue(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(len(queryset), 1)

    @freeze_time("2023-12-12 21:00:00")
    def test_rushana_has_permissions_by_date_and_time(self):
        self.staff_user.groups.add(self.group)

        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )
        assign_perm('view_mother', self.rushana, mother)
        assign_perm('change_mother', self.rushana, mother)

        request = self.factory.get('/')
        request.user = self.rushana

        filter_instance = AuthConditionListFilter(
            request, {'date_or_time': 'by_date_and_time'}, Mother, self.mother_admin_instance
        )

        lookups = filter_instance.lookups(request, self.mother_admin_instance)
        self.assertTrue(lookups)

        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))
        self.assertEqual(len(queryset), 1)
