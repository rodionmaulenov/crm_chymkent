from datetime import time, date

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
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

    def test_condition_with_comment_or_planned_and_finished(self):
        Comment.objects.create(mother=self.mother, description='Non-empty comment')
        Condition.objects.create(mother=self.mother, finished=True, condition=Condition.ConditionChoices.NO_BABY)

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('has not baby', result)

    def test_unfinished_condition_without_date(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=None)

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(
            f'href="/admin/mothers/condition/{condition.id}/change/?mother={condition.id}&_changelist_filters=%2F"',
            result)

    def test_unfinished_condition_with_date_and_unfiltered_view(self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('<strong>recently created</strong>/ <br> 9 Jan', result)

    @freeze_time("2023-12-12")
    def test_unfinished_condition_with_date_on_change_list_page(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'/admin/mothers/condition/{condition.pk}/change/', result)

    @freeze_time("2024-12-12 20:00:00")
    def test_unfinished_condition_with_datetime_on_change_list_page(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 12, 12),
                                             scheduled_time=time(21, 20))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'/admin/mothers/condition/{condition.pk}/change/', result)

    def test_unfinished_condition_with_datetime_and_unfiltered_view(self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9),
                                 scheduled_time=time(20, 20))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'<strong>recently created</strong>/ <br> 9 Jan 20:20', result)

    def test_finished_condition(self):
        Condition.objects.create(mother=self.mother, finished=True)

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(
            f'/admin/mothers/condition/add/?mother={self.mother.id}&_changelist_filters',
            result)

    def test_filtered_view_based_on_condition_criteria_with_date(self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('<strong>recently created</strong>/ <br> 9 Jan', result)

    def test_filtered_view_based_on_condition_criteria_with_datetime(self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9),
                                 scheduled_time=time(20, 20))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('<strong>recently created</strong>/ <br> 9 Jan 20:20', result)

    def test_mother_with_no_conditions(self):
        mother = self.mother

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        with self.assertRaises(AttributeError):
            self.mother_admin.create_condition_link(obj=mother)

    def test_mother_with_multiple_conditions(self):
        Condition.objects.create(mother=self.mother, finished=True)
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 10))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('<strong>recently created</strong>/ <br> 10 Jan', result)
