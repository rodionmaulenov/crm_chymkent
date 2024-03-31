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
Stage: models


class HasChangePermissionTest(TestCase):
    def setUp(self):
        self.admin = BanAdmin(Ban, admin.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='mother')
        self.ban = Ban.objects.create(mother=self.mother, comment='some reason', banned=False)

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_super_user_has_perm_obj(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_change_permission(request, self.ban)

        self.assertTrue(view)

    def test_super_user_has_perm_list_layer(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_change_permission(request)

        self.assertTrue(view)

    def test_staff_has_perm_obj(self):
        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin, obj=self.ban)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request, self.ban)

        self.assertTrue(view)

    def test_staff_has_perm_list_layer(self):
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.BAN, finished=False)

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin, obj=self.ban)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request)

        self.assertTrue(view)

    def test_staff_assign_model_perm_obj(self):
        view_permission = Permission.objects.get(codename='change_ban')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request, self.ban)

        self.assertTrue(view)

    def test_staff_assign_model_perm_list_layer(self):
        view_permission = Permission.objects.get(codename='change_ban')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request)

        self.assertTrue(view)

    def test_staff_user_has_not_any_perms(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_view_permission(request)

        self.assertFalse(view)
