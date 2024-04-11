from django.contrib import admin
from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models

from gmail_messages.services.manager_factory import ManagerFactory

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
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_super_user_can_add(self):
        request = self.factory.get('/')
        request.user = self.superuser
        add = self.admin.has_add_permission(request)

        self.assertTrue(add)

    def test_staff_user_can_add_with_model_lvl_perm(self):
        view_permission = Permission.objects.get(codename='add_ban')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        add = self.admin.has_add_permission(request)

        self.assertTrue(add)

    def test_staff_user_can_add_with_obj_assign_perm(self):
        mother = Mother.objects.create(name='Mother 1')

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin, obj=mother)

        request = self.factory.get('/')
        request.user = self.staff_user
        add = self.admin.has_add_permission(request)

        self.assertTrue(add)

    def test_staff_user_can_not_add(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        add = self.admin.has_add_permission(request)

        self.assertFalse(add)
