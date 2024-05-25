from django.contrib import admin
from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.admin import DocumentAdmin
from documents.models import MainDocument
from gmail_messages.services.manager_factory import ManagerFactory

from mothers.models import Mother, Stage

User = get_user_model()
Mother: models
Stage: models
MainDocument: models


class HasChangePermissionTest(TestCase):
    def setUp(self):
        self.admin = DocumentAdmin(MainDocument, admin.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='mother')
        self.mock_file = SimpleUploadedFile('test.txt', b'This is a test file', content_type='text/plain')
        self.document = MainDocument.objects.create(mother=self.mother, file=self.mock_file, note='some', title='some')

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_super_user_has_not_perm_if_obj(self):
        request = self.factory.get('/')
        request.user = self.superuser
        change = self.admin.has_change_permission(request, self.document)

        self.assertFalse(change)

    def test_super_user_has_not_perm_list_layer(self):
        request = self.factory.get('/')
        request.user = self.superuser
        change = self.admin.has_change_permission(request)

        self.assertFalse(change)

    def test_staff_has_not_perm_if_obj(self):
        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin, obj=self.document)

        request = self.factory.get('/')
        request.user = self.staff_user
        change = self.admin.has_change_permission(request, self.document)

        self.assertFalse(change)

    def test_staff_has_not_perm_list_layer(self):
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.BAN, finished=False)

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin, obj=self.document)

        request = self.factory.get('/')
        request.user = self.staff_user
        change = self.admin.has_change_permission(request)

        self.assertFalse(change)

    def test_staff_assign_model_perm_if_obj(self):
        view_permission = Permission.objects.get(codename='change_document')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        change = self.admin.has_change_permission(request, self.document)

        self.assertFalse(change)

    def test_staff_assign_model_perm_list_layer(self):
        view_permission = Permission.objects.get(codename='change_document')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user
        change = self.admin.has_change_permission(request)

        self.assertFalse(change)
