from datetime import time, date

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.urls import reverse
from freezegun import freeze_time

from mothers.models import Mother, Comment, Condition
from mothers.admin import MotherAdmin

Mother: models
Comment: models
Condition: models

User = get_user_model()


class CreateConditionLinkTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(username='superuser', password='password')
        cls.mother = Mother.objects.create(name='Test')

    def setUp(self):
        self.factory = RequestFactory()
        self.mother_admin = MotherAdmin(Mother, AdminSite())

    def test_when_exist_another_related_to_mother_instance(self):
        Comment.objects.create(mother=self.mother, description='Non-empty comment')
        Condition.objects.create(mother=self.mother, finished=True, condition=Condition.ConditionChoices.NO_BABY)

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('has not baby', result)

    def test_can_change_already_existing_condition_on_change_list_page(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=None)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(
            f'href="/admin/mothers/condition/{condition.pk}/change/?mother={condition.pk}&_changelist_filters=%2F"',
            result)

    @freeze_time("2023-12-12")
    def test_can_not_change_on_change_list_page_when_condition_on_filtered_changelist_page(self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('<strong>recently created</strong>/<br>12 Dec', result)

    def test_mother_with_multiple_conditions(self):
        Condition.objects.create(mother=self.mother, finished=True)
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 10))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('<strong>recently created</strong>/<br>10 Jan', result)

    @freeze_time("2023-12-12")
    def test_can_not_change_on_change_list_page_when_condition_on_filtered_changelist_page_version2(self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 11))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('<strong>recently created</strong>/<br>11 Dec', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_can_not_change_on_change_list_page_when_condition_on_filtered_changelist_page_version3(self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12),
                                 scheduled_time=time(21, 20))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('<strong>recently created</strong>/ <br> 12 Dec', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_can_not_change_on_change_list_page_when_condition_on_filtered_changelist_page_version4(self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12),
                                 scheduled_time=time(22, 00))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('<strong>recently created</strong>/<br>12 Dec', result)

    @freeze_time("2023-12-12")
    def test_can_change_on_change_list_page_when_condition_on_filtered_changelist_page(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 13))

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'href="/admin/mothers/condition/{condition.pk}/change/"', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_can_change_on_change_list_page_when_condition_on_filtered_changelist_page_version2(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12),
                                             scheduled_time=time(23, 20))

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'href="/admin/mothers/condition/{condition.pk}/change/"', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_can_not_change_on_change_list_page_when_condition_on_filtered_changelist_page_version3(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 13),
                                             scheduled_time=time(23, 00))

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'href="/admin/mothers/condition/{condition.pk}/change/"', result)

    def test_finished_condition_can_add_new_condition(self):
        Condition.objects.create(mother=self.mother, finished=True)

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(
            f'/admin/mothers/condition/add/?mother={self.mother.id}&_changelist_filters',
            result)

    def test_mother_with_no_conditions(self):
        mother = self.mother

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        with self.assertRaises(AttributeError):
            self.mother_admin.create_condition_link(obj=mother)

    def test_can_change_on_filtered_mother_change_list_url_by_date(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 10))

        change_url = reverse('admin:mothers_mother_changelist')
        request = self.factory.get(change_url, {'date_or_time': 'by_date'})
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'href="/admin/mothers/condition/{condition.pk}/change/" class="violet-link">', result)

    def test_can_change_on_filtered_mother_change_list_url_by_date_and_time(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 10))

        change_url = reverse('admin:mothers_mother_changelist')
        request = self.factory.get(change_url, {'date_or_time': 'by_date_and_time'})
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'href="/admin/mothers/condition/{condition.pk}/change/" class="violet-link">', result)
