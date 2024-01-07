from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import models

from mothers.admin import MotherAdmin
from mothers.models import Mother, Comment, Planned

User = get_user_model()

Mother: models
Planned: models
Comment: models


class GetActionMethodTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username='user', password='user', is_staff=True)
        self.superuser = User.objects.create_superuser(username='superuser', password='user')

        admin_site = AdminSite()
        self.mother_admin = MotherAdmin(Mother, admin_site)
        self.request_factory = RequestFactory()

    def test_actions_banned_superuser_access(self):
        request = self.request_factory.get('/')
        request.user = self.superuser

        actions = self.mother_admin.get_actions(request)
        self.assertIn('banned', actions)

    def test_actions_staff_without_permission(self):
        request = self.request_factory.get('/')
        request.user = self.staff_user

        actions = self.mother_admin.get_actions(request)
        self.assertNotIn('banned', actions)

    def test_actions_staff_with_permission(self):
        banned_mother_permission = Permission.objects.get(codename='move_to_ban')
        self.staff_user.user_permissions.add(banned_mother_permission)
        request = self.request_factory.get('/')
        request.user = self.staff_user

        actions = self.mother_admin.get_actions(request)
        self.assertIn('banned', actions)

    def test_banned_exists_when_Mother_instance_have_related_Comment_instance_with_description(self):
        request = self.request_factory.get('/')
        request.user = self.superuser

        mother = Mother.objects.create(name='Test 1')
        Comment.objects.create(mother=mother, description='some reason')

        actions = self.mother_admin.get_actions(request)
        self.assertIn('banned', actions)

    def test_banned_exists_when_Mother_instance_not_have_related_Comment_instance_with_description(self):
        request = self.request_factory.get('/')
        request.user = self.superuser

        Mother.objects.create(name='Test 1')

        actions = self.mother_admin.get_actions(request)
        self.assertNotIn('banned', actions)

    def test_actions_first_visit_superuser_access(self):
        request = self.request_factory.get('/')
        request.user = self.superuser

        actions = self.mother_admin.get_actions(request)
        self.assertIn('first_visit_stage', actions)

    def test_actions_first_visit_staff_without_permission(self):
        request = self.request_factory.get('/')
        request.user = self.staff_user

        actions = self.mother_admin.get_actions(request)
        self.assertNotIn('first_visit_stage', actions)

    def test_actions_first_visit_staff_with_permission(self):
        transfer_on_first_visit_permission = Permission.objects.get(codename='action_first_visit')
        self.staff_user.user_permissions.add(transfer_on_first_visit_permission)
        request = self.request_factory.get('/')
        request.user = self.staff_user

        actions = self.mother_admin.get_actions(request)
        self.assertIn('first_visit_stage', actions)

    def test_banned_exists_when_Mother_instance_have_related_Planned_instance_with_plan_and_finished_False(self):
        request = self.request_factory.get('/')
        request.user = self.superuser

        mother = Mother.objects.create(name='Test 1')
        Planned.objects.create(mother=mother, plan=Planned.PlannedChoices.TAKE_TESTS, finished=False)

        actions = self.mother_admin.get_actions(request)
        self.assertIn('first_visit_stage', actions)

    def test_banned_exists_when_Mother_instance_not_have_related_Planned_instance(self):
        request = self.request_factory.get('/')
        request.user = self.superuser

        Mother.objects.create(name='Test 1')

        actions = self.mother_admin.get_actions(request)
        self.assertNotIn('first_visit_stage', actions)
