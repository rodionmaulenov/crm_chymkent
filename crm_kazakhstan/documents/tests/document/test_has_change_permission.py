from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from documents.admin import DocumentProxyAdmin
from documents.models import Document

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

User = get_user_model()


class HasChangePermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.mother_admin = MotherAdmin(Mother, self.site)
        self.document_admin = DocumentProxyAdmin(Document, self.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='Mother 1')
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_super_user_has_obj_perm(self):
        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.superuser
        view = self.document_admin.has_change_permission(request, self.mother)

        self.assertTrue(view)

    def test_super_user_has_list_perm(self):
        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.superuser
        view = self.document_admin.has_change_permission(request)

        self.assertTrue(view)

    def test_staff_user_has_obj_perm_with_custom_perm(self):
        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.mother_admin, obj=self.mother)

        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        view = self.document_admin.has_change_permission(request, self.mother)

        self.assertTrue(view)

    def test_staff_user_has_list_perm_with_custom_perm(self):
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY)

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.mother_admin, obj=self.mother)

        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        view = self.document_admin.has_change_permission(request)

        self.assertTrue(view)

    def test_staff_user_has_obj_perm_with_base_document_perm(self):
        view_permission = Permission.objects.get(codename='change_document')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        view = self.document_admin.has_change_permission(request, self.mother)

        self.assertTrue(view)

    def test_staff_user_has_list_perm_with_base_document_perm(self):
        view_permission = Permission.objects.get(codename='change_document')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        view = self.document_admin.has_change_permission(request)

        self.assertTrue(view)

    def test_staff_user_has_not_obj_perm(self):
        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        view = self.document_admin.has_change_permission(request, self.mother)

        self.assertFalse(view)

    def test_staff_user_has_not_list_perm(self):
        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        view = self.document_admin.has_change_permission(request)

        self.assertFalse(view)

    def test_staff_user_has_not_list_perm_without_query_param(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.document_admin.has_change_permission(request)

        self.assertFalse(view)

    def test_staff_user_has_not_obj_perm_without_query_param(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.document_admin.has_change_permission(request, self.mother)

        self.assertFalse(view)
