from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from guardian.shortcuts import assign_perm

from mothers.models import Mother, Condition
from mothers.admin import ConditionAdmin

User = get_user_model()
Mother: models
Condition: models


class HasViePermissionMethodTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ConditionAdmin(Condition, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

        self.rushana = User.objects.create_user(username='Rushana', password='password', is_staff=True)

    def test_super_user_has_view_perm(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_view_permission(request)

        self.assertFalse(view)

    def test_super_user_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = Condition.objects.create(mother=mother)
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_view_permission(request, condition)

        self.assertTrue(view)

    def test_staff_user_has_not_view_perm(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request)

        self.assertFalse(view)

    def test_rushana_has_not_view_perm(self):
        request = self.factory.get('/')
        request.user = self.rushana
        view = self.admin.has_view_permission(request)

        self.assertFalse(view)

    def test_rushana_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = Condition.objects.create(mother=mother)
        assign_perm('view_condition', self.rushana, condition)

        # Simulate a request with the user
        request = self.factory.get('/admin/mothers/condition/')
        request.user = self.rushana

        self.assertTrue(self.admin.has_view_permission(request, condition))

    def test_rushana_has_not_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = Condition.objects.create(mother=mother)
        request = self.factory.get('/')
        request.user = self.rushana
        view = self.admin.has_view_permission(request, condition)

        self.assertFalse(view)
