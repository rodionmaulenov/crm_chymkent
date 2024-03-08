from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from guardian.shortcuts import assign_perm

from mothers.models import Mother, Stage, State
from mothers.admin import StateAdmin

User = get_user_model()
Mother: models
Stage: models


class HasAddPermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = StateAdmin(State, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True)

    def test_super_user_has_perm(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_add_permission(request)

        self.assertTrue(view)

    def test_staff_has_perm(self):
        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        assign_perm('primary_stage', self.staff_user, mother)

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertTrue(self.admin.has_add_permission(request))

    def test_staff_has_perm_with_model_lvl_perm(self):
        Mother.objects.create(name='Mother 1')

        view_permission = Permission.objects.get(codename='add_state')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertTrue(self.admin.has_add_permission(request))

    def test_staff_has_not_add_perm(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_add_permission(request)

        self.assertFalse(view)
