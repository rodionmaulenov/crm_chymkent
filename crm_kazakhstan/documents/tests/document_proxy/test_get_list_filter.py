from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from documents.admin import DocumentProxyAdmin
from documents.filters import OnWhatStageFilter
from documents.models import DocumentProxy

User = get_user_model()


class TestGetListFilter(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.admin = DocumentProxyAdmin(DocumentProxy, self.admin_site)
        self.factory = RequestFactory()

        # Create a superuser
        self.superuser = User.objects.create_superuser(username='superadmin', password='superadmin',
                                                       email='superadmin@example.com')

        # Create a regular user
        self.user_with_perm = User.objects.create_user(username='user_with_perm', password='password',
                                                       email='user_with_perm@example.com')
        view_permission = Permission.objects.get(codename='view_documentproxy')
        self.user_with_perm.user_permissions.add(view_permission)

        # Create a user without the permission
        self.user_without_perm = User.objects.create_user(username='user_without_perm', password='password',
                                                          email='user_without_perm@example.com')

    def test_get_filter_list_with_permission(self):
        request = self.factory.get('/')
        request.user = self.user_with_perm

        filters = self.admin.get_list_filter(request)

        self.assertEqual(filters, ('created', OnWhatStageFilter))

    def test_get_filter_list_without_permission(self):
        request = self.factory.get('/')
        request.user = self.user_without_perm

        filters = self.admin.get_list_filter(request)

        self.assertEqual(filters, ('created',))

