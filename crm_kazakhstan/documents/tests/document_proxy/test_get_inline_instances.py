from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from documents.admin import DocumentProxyAdmin
from documents.inlines.main import DocumentInline
from documents.inlines.required import DocumentRequiredInline
from documents.models import DocumentProxy

from mothers.models import Mother

User = get_user_model()


class TestDocumentProxyAdminInlines(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.admin = DocumentProxyAdmin(DocumentProxy, self.admin_site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')
        self.staff_user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')
        self.client.login(username='admin', password='admin')

    def test_main_document_inline_names(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        inline_instances = self.admin.get_inline_instances(request, obj=self.mother)

        main_document_inline = next(inline for inline in inline_instances if isinstance(inline, DocumentInline))
        self.assertEqual(main_document_inline.verbose_name, 'Main Document')
        self.assertEqual(main_document_inline.verbose_name_plural, 'Main Documents')

    def test_acquired_document_inline_names(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        inline_instances = self.admin.get_inline_instances(request, obj=self.mother)

        acquired_document_inline = next(
            inline for inline in inline_instances if isinstance(inline, DocumentRequiredInline))
        self.assertEqual(acquired_document_inline.verbose_name, 'Required Document')
        self.assertEqual(acquired_document_inline.verbose_name_plural, 'Required Documents')
