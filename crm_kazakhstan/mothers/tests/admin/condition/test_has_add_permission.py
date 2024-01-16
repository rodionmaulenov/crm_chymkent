from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from guardian.shortcuts import assign_perm

from mothers.models import Mother, Condition, Stage
from mothers.admin import ConditionAdmin

User = get_user_model()
Mother: models
Stage: models
Condition: models


class HasViePermissionMethodTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ConditionAdmin(Condition, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)
        self.rushana = User.objects.create_user(username='Rushana', password='password')

    def test_super_user_has_add_perm(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_add_permission(request)

        self.assertTrue(view)

    def test_staff_user_has_not_add_perm(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_add_permission(request)

        self.assertFalse(view)

    def test_rushana_has_not_add_perm(self):
        request = self.factory.get('/')
        request.user = self.rushana
        view = self.admin.has_add_permission(request)

        self.assertFalse(view)

    def test_rushana_has_add_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)

        assign_perm('view_mother', self.rushana, mother)
        assign_perm('change_mother', self.rushana, mother)

        request = self.factory.get('/')
        request.user = self.rushana

        view = self.admin.has_add_permission(request)
        self.assertTrue(view)
