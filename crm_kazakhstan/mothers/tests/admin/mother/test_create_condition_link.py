from datetime import time, date
from freezegun import freeze_time

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models

from mothers.models import Mother, Comment, Condition, Planned
from mothers.admin import MotherAdmin

Mother: models
Comment: models
Condition: models
Planned: models

User = get_user_model()


class CreateConditionLinkTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name='Test')
        self.factory = RequestFactory()
        self.mother_admin = MotherAdmin(Mother, AdminSite())
        self.superuser = User.objects.create_superuser(username='superuser', password='password')

    def test_Comment_instance_exists(self):
        Comment.objects.create(mother=self.mother, description='Non-empty comment')
        Condition.objects.create(mother=self.mother, finished=True, condition=Condition.ConditionChoices.NO_BABY)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('has not baby', result)

    def test_Planned_instance_exists(self):
        Planned.objects.filter(mother=self.mother, plan=Planned.PlannedChoices.TAKE_TESTS, finished=False)
        Condition.objects.create(mother=self.mother, finished=True, condition=Condition.ConditionChoices.NO_BABY)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('has not baby', result)

    def test_Comment_and_Planned_instance_not_exist_user_can_add_new_Condition_instance(self):
        Condition.objects.create(mother=self.mother, finished=True, condition=Condition.ConditionChoices.NO_BABY)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'/admin/mothers/condition/add/?mother={self.mother.pk}&_changelist_filters=%2F', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_can_change_on_change_list_page_when_Condition_instance_not_on_filtered_changelist_page(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 15),
                                             scheduled_time=time(21, 20, 0),
                                             condition=Condition.ConditionChoices.CREATED)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'"/admin/mothers/condition/{condition.pk}/change/" class="light-green"', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_can_not_change_on_change_list_page_when_Condition_instance_on_filtered_changelist_page(self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12),
                                 scheduled_time=time(21, 20, 0), condition=Condition.ConditionChoices.__empty__,
                                 reason='some reason')

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn('<strong>some reason</strong>', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_can_change_on_change_list_page_when_condition_not_yet_on_filtered_changelist_page(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12),
                                             scheduled_time=time(23, 20), condition=Condition.ConditionChoices.CREATED)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'"/admin/mothers/condition/{condition.pk}/change/" class="light-green">'
                      '<strong>recently created</strong></a>', result)

    @freeze_time("2023-12-12 22:00:00")
    def test_can_change_on_change_list_page_when_condition_on_filtered_changelist_page(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12),
                                             scheduled_time=time(21, 20, 0), reason='some reason')

        request = self.factory.get('/admin/mothers/mother/?planned_time=datetime')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.mother_admin.request = request

        result = self.mother_admin.create_condition_link(obj=self.mother)

        self.assertIn(f'"/admin/mothers/condition/{condition.pk}/change/" class="violet-link"', result)
