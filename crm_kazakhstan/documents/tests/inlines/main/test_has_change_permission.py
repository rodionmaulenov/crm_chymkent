from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from documents.inlines.main import MainInline
from documents.models import Mother

User = get_user_model()


class DocumentInlinePermissionTests(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.inline = MainInline(Mother, self.admin_site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')
        self.superuser = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')
        self.view_user = User.objects.create_user(username='viewer', password='viewer', email='viewer@example.com')
        view_permission = Permission.objects.get(codename='view_document')
        self.view_user.user_permissions.add(view_permission)

    def test_has_change_permission_no_get_params(self):
        request = self.factory.get('/admin/documents/')
        request.user = self.superuser
        has_permission = self.inline.has_change_permission(request, obj=self.mother)
        self.assertFalse(has_permission)

    def test_has_change_permission_superuser(self):
        request = self.factory.get('/admin/documents/?someparam=1')
        request.user = self.superuser
        has_permission = self.inline.has_change_permission(request, obj=self.mother)
        self.assertTrue(has_permission)

    def test_has_change_permission_view_only_user(self):
        request = self.factory.get('/admin/documents/?someparam=1')
        request.user = self.view_user
        has_permission = self.inline.has_change_permission(request, obj=self.mother)
        self.assertFalse(has_permission)

    def test_has_change_permission_normal_user(self):
        normal_user = User.objects.create_user(username='normal', password='normal', email='normal@example.com')
        request = self.factory.get('/admin/documents/?someparam=1')
        request.user = normal_user
        has_permission = self.inline.has_change_permission(request, obj=self.mother)
        self.assertTrue(has_permission)
