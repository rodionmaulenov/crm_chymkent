from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from documents.admin import DocumentProxyAdmin
from documents.models import DocumentProxy

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin


User = get_user_model()
Mother: models


class HasChangePermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.mother_admin = MotherAdmin(Mother, self.site)
        self.document_admin = DocumentProxyAdmin(DocumentProxy, self.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='Mother 1')
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_superuser_has_access(self):
        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.superuser
        access = self.document_admin.has_change_permission(request)

        self.assertTrue(access)

    def test_staff_has_access_with_custom_perm_on_primary_stage(self):
        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.mother_admin, obj=self.mother, user=self.staff_user)

        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        access = self.document_admin.has_change_permission(request)
        self.assertTrue(access)


    def test_staff_has_access_with_base_perm(self):
        view_permission = Permission.objects.get(codename='change_documentproxy')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        access = self.document_admin.has_change_permission(request)

        self.assertTrue(access)

    def test_staff_has_not_access(self):
        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        access = self.document_admin.has_change_permission(request)

        self.assertFalse(access)
