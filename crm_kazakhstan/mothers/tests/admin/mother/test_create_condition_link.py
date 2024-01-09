from datetime import time, date, datetime

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import Mother, Comment, Condition
from mothers.admin import MotherAdmin

Mother: models
Comment: models
Condition: models

User = get_user_model()


class CreateConditionLinkTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mother_admin = MotherAdmin(Mother, AdminSite())
        self.superuser = User.objects.create_superuser(username='superuser', password='password')

    def test_condition_with_comment_or_planned_and_finished(self):
        mother = Mother.objects.create(name='Test')
        Comment.objects.create(mother=mother, description='Non-empty comment')
        Condition.objects.create(mother=mother, finished=True, condition=Condition.ConditionChoices.NO_BABY)

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=mother)

        self.assertIn('has not baby', result)

    def test_unfinished_condition_without_date(self):
        mother = Mother.objects.create(name='Test')
        Condition.objects.create(mother=mother, finished=False, scheduled_date=None)

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=mother)

        self.assertIn(f'href="/admin/mothers/condition/{mother.id}/change/?mother={mother.id}&_changelist_filters=%2F"',
                      result)

    def test_unfinished_condition_with_date_and_unfiltered_view(self):
        mother = Mother.objects.create(name='Test')
        Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2024, 1, 9))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=mother)

        self.assertIn('<strong>recently created</strong>/ <br> 9 Jan', result)

    def test_unfinished_condition_with_datetime_and_unfiltered_view(self):
        mother = Mother.objects.create(name='Test')
        Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2024, 1, 9),
                                 scheduled_time=time(20, 20))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=mother)

        self.assertIn(f'<strong>recently created</strong>/ <br> 9 Jan 20:20', result)

    def test_finished_condition(self):
        mother = Mother.objects.create(name='Test')
        Condition.objects.create(mother=mother, finished=True)

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=mother)

        self.assertIn(
            f'/admin/mothers/condition/add/?mother={mother.id}&_changelist_filters',
            result)

    def test_filtered_view_based_on_condition_criteria_with_date(self):
        mother = Mother.objects.create(name='Test')
        Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2024, 1, 9))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=mother)

        self.assertIn('<strong>recently created</strong>/ <br> 9 Jan', result)

    def test_filtered_view_based_on_condition_criteria_with_datetime(self):
        mother = Mother.objects.create(name='Test')
        Condition.objects.create(mother=mother, finished=False, scheduled_date=date(2024, 1, 9),
                                 scheduled_time=time(20, 20))

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=mother)

        self.assertIn('<strong>recently created</strong>/ <br> 9 Jan 20:20', result)

    def test_mother_with_no_conditions(self):
        mother = Mother.objects.create(name='Test')

        request = self.factory.get('/')
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=mother)
        print(result)

        # Replace 'expected_result' with the expected output
        expected_result = 'Default message or link'
        self.assertEqual(result, expected_result)

