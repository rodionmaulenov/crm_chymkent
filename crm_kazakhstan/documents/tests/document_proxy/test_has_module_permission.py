from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import models
from django.contrib import admin

from documents.admin import DocumentProxyAdmin
from documents.models import DocumentProxy

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

User = get_user_model()
Stage: models
Mother: models


class HasModulePermissionTest(TestCase):
    def setUp(self):
        self.mother_admin = MotherAdmin(Mother, admin.site)
        self.document_admin = DocumentProxyAdmin(DocumentProxy, admin.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='Mother 1')

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_superuser_has_access(self):
        request = self.factory.get('/')
        request.user = self.superuser
        access = self.document_admin.has_module_permission(request)

        self.assertTrue(access)

    def test_staff_has_access_with_custom_perm_on_primary_stage(self):
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY)

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.mother_admin, obj=self.mother, user=self.staff_user)

        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.document_admin.has_module_permission(request)
        self.assertTrue(access)

    def test_staff_has_access_with_custom_perm_on_first_visit_stage(self):
        staff_user2 = User.objects.create(username='staff_user2', password='password', is_staff=True,
                                          stage=Stage.StageChoices.FIRST_VISIT)

        mother = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT)

        factory = ManagerFactory()
        first_visit_manager = factory.create('FirstVisitStageManager')
        first_visit_manager.assign_user(content_type=self.mother_admin, obj=mother, user=staff_user2)

        request = self.factory.get('/')
        request.user = staff_user2
        access = self.document_admin.has_module_permission(request)
        self.assertTrue(access)

    def test_staff_has_access_with_base_perm(self):
        view_permission = Permission.objects.get(codename='view_documentproxy')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.document_admin.has_module_permission(request)

        self.assertTrue(access)

    def test_staff_has_not_access(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.document_admin.has_module_permission(request)

        self.assertFalse(access)
