from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from documents.inlines.main import DocumentInline
from documents.models import Mother

User = get_user_model()


class DocumentInlinePermissionTests(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.inline = DocumentInline(Mother, self.admin_site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')
        self.staff_user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')

    def test_has_view_permission(self):
        request = self.factory.get('/admin/documents/')
        request.user = self.staff_user
        has_permission = self.inline.has_view_permission(request, obj=self.mother)
        self.assertTrue(has_permission)

