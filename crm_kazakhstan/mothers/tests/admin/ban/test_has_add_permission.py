from guardian.shortcuts import assign_perm

from django.contrib import admin
from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from mothers.admin import BanAdmin
from mothers.models import Mother, Ban, Stage

User = get_user_model()
Mother: models
Ban: models


class HasAddPermissionTest(TestCase):
    def setUp(self):
        self.admin = BanAdmin(Ban, admin.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True)

    def test_super_user_can_add(self):
        ban_add_url = reverse('admin:mothers_ban_add')
        request = self.factory.get(ban_add_url)
        request.user = self.superuser
        view = self.admin.has_add_permission(request)

        self.assertTrue(view)

    def test_super_user_can_not_add(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_add_permission(request)

        self.assertFalse(view)

    def test_staff_user_can_add_with_model_lvl_perm(self):
        view_permission = Permission.objects.get(codename='add_mother')
        self.staff_user.user_permissions.add(view_permission)

        ban_add_url = reverse('admin:mothers_ban_add')
        request = self.factory.get(ban_add_url)
        request.user = self.staff_user
        view = self.admin.has_add_permission(request)

        self.assertTrue(view)

    def test_staff_user_can_add_with_obj_assign_perm(self):
        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)

        assign_perm('primary_stage', self.staff_user, mother)

        ban_add_url = reverse('admin:mothers_ban_add')
        request = self.factory.get(ban_add_url)
        request.user = self.staff_user
        view = self.admin.has_add_permission(request)

        self.assertTrue(view)

    def test_staff_user_can_not_add(self):
        ban_change_list_url = reverse('admin:mothers_ban_changelist')
        request = self.factory.get(ban_change_list_url)
        request.user = self.superuser
        view = self.admin.has_add_permission(request)

        self.assertFalse(view)