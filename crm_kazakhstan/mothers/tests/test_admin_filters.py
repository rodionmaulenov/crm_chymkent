from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.contrib.auth.models import Permission
from mothers.models import Condition, Mother
from mothers.admin import MotherAdmin
from mothers.filters import ConditionListFilter

from datetime import datetime, timezone, time
from freezegun import freeze_time

MotherAdmin: admin.ModelAdmin
Condition: models
Mother: models
User = get_user_model()


class ConditionListFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(username='testuser', password='testpassword', is_staff=True,
                                                  is_superuser=True)
        self.staff_user = User.objects.create_user(username='staffuser', password='staffuserpassword', is_staff=True)
        self.user = User.objects.create_user(username='user', password='userpassword')

        self.mother = Mother.objects.create(
            id=1,
            name='Test Mother',
            number='123',
            program='Test Program',
            residence='Test Residence',
            height_and_weight='Test Height and Weight',
        )

        self.mother2 = Mother.objects.create(
            id=2,
            name='Test2 Mother',
            number='1234',
            program='Test2 Program',
            residence='Test2 Residence',
            height_and_weight='Test2 Height and Weight',
        )

        self.mother3 = Mother.objects.create(
            id=3,
            name='Test3 Mother',
            number='12345',
            program='Test3 Program',
            residence='Test3 Residence',
            height_and_weight='Test3 Height and Weight',
        )

        self.condition_smaller_date = Condition.objects.create(
            mother=self.mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            condition='FR3'
        )
        self.condition_equal_date = Condition.objects.create(
            mother=self.mother2,
            scheduled_date=datetime(2023, 12, 13, tzinfo=timezone.utc),
            condition='FR2'
        )

        self.condition_date_and_time = Condition.objects.create(
            mother=self.mother3,
            scheduled_date=datetime(2023, 12, 10, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            condition='SC'
        )

        self.factory = RequestFactory()

        self.admin_site = AdminSite()
        self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)

    @freeze_time("2023-12-12")
    def test_filter_if_date_condition_smaller(self):
        request = self.factory.get('/admin/mothers/mother/')
        request.user = self.user
        request.GET = {'date_or_time': 'by_date'}
        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1, msg='must be 1 instances because planed dates smaller than date today')

    @freeze_time("2023-12-13")
    def test_filter_if_date_condition_equal(self):
        request = self.factory.get('/admin/mothers/mother/')
        request.user = self.user
        request.GET = {'date_or_time': 'by_date'}
        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 2,
                         msg='must be 2 instances because planed dates equal date today')

    @freeze_time("2023-12-10")
    def test_filter_if_date_condition_bigger(self):
        request = self.factory.get('/admin/mothers/mother/')
        request.user = self.user
        request.GET = {'date_or_time': 'by_date'}
        filter_instance = ConditionListFilter(
            request, {'date_or_time': 'by_date'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0,
                         msg='must be 0 instances because planed dates bigger than date today')

    @freeze_time("2023-12-10 14:30:00")
    def test_filter_if_time_condition_equal(self):
        request = self.factory.get('/admin/mothers/mother/')
        request.user = self.user
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(request, {'date_or_time': 'by_date_and_time'},
                                              Mother, self.mother_admin_instance)
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1, msg='must be 1 instances because planed time equal time now')

    @freeze_time("2023-12-10 20:30:00")
    def test_filter_if_time_condition_smaller(self):
        request = self.factory.get('/admin/mothers/mother/')
        request.user = self.user
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(request, {'date_or_time': 'by_date_and_time'},
                                              Mother, self.mother_admin_instance)
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1, msg='must be 1 instances because planed time less time now')

    @freeze_time("2023-12-01 20:30:00")
    def test_filter_if_time_condition_bigger(self):
        request = self.factory.get('/admin/mothers/mother/')
        request.user = self.user
        request.GET = {'date_or_time': 'by_date_and_time'}

        filter_instance = ConditionListFilter(request, {'date_or_time': 'by_date_and_time'},
                                              Mother, self.mother_admin_instance)
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0, msg='must be 0 instances because planed time bigger than time now')

    @freeze_time("2023-12-11 20:10:00")
    def test_access_admin_interface_filtering_via_superuser_by_time(self):
        self.client.force_login(self.superuser)
        response = self.client.get('/admin/mothers/mother/', {'date_or_time': 'by_date_and_time'})

        self.assertEqual(response.status_code, 200, msg='User should have access to the admin interface')
        self.assertContains(response, 'Entries by Time')

        response = self.client.get('/admin/mothers/mother/', {'date_or_time': 'by_date'})
        self.assertContains(response, 'Entries by Date')

        self.client.logout()

    @freeze_time("2023-12-11 20:10:00")
    def test_disable_access_admin_interface_filtering_via_is_staff(self):
        self.client.force_login(self.staff_user)
        response = self.client.get('/admin/mothers/mother/', {'date_or_time': 'by_date'})
        self.assertEqual(response.status_code, 403, msg='User should not have access to view the admin interface')
        response = self.client.get('/admin/mothers/mother/', {'date_or_time': 'by_date_and_time'})
        self.assertEqual(response.status_code, 403, msg='User should not have access to view the admin interface')

        self.client.logout()

    @freeze_time("2023-12-11 20:10:00")
    def test_disable_access_admin_interface_filtering(self):
        self.client.force_login(self.user)
        response = self.client.get('/admin/mothers/mother/',
                                   {'date_or_time': 'by_date'})
        self.assertEqual(response.status_code, 302,
                         msg='User should not have access to view the admin interface and not the staff and superuser')

        self.client.logout()

    @freeze_time("2023-12-11 20:10:00")
    def test_access_admin_interface(self):
        can_view_mother_permission = Permission.objects.get(
            codename='view_mother')
        self.staff_user.user_permissions.add(can_view_mother_permission)

        self.client.force_login(self.staff_user)
        response = self.client.get('/admin/mothers/mother/', {'date_or_time': 'by_date'})
        self.assertEqual(response.status_code, 200, msg='Staff User should have access to view the admin interface')
        self.assertNotContains(response, 'Entries by Date')
        response = self.client.get('/admin/mothers/mother/', {'date_or_time': 'by_date_and_time'})
        self.assertNotContains(response, 'Entries by Time')

        self.client.logout()

    @freeze_time("2023-12-11 20:10:00")
    def test_access_admin_interface_filtering_via_is_staff_view_and_main_permission(self):
        can_view_mother_permission = Permission.objects.get(
            codename='view_mother')
        can_view_condition_filter_permission = Permission.objects.get(
            codename='main_manager_condition_filter_option')
        self.staff_user.user_permissions.add(can_view_mother_permission, can_view_condition_filter_permission)

        self.client.force_login(self.staff_user)
        response = self.client.get('/admin/mothers/mother/', {'date_or_time': 'by_date'})
        self.assertEqual(response.status_code, 200, msg='Staff User should have access to view the admin interface')
        self.assertContains(response, 'Entries by Date')
        response = self.client.get('/admin/mothers/mother/', {'date_or_time': 'by_date_and_time'})
        self.assertContains(response, 'Entries by Time')

        self.client.logout()
