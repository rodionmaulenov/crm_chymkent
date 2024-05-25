from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from documents.admin import DocumentProxyAdmin
from documents.inlines.main import DocumentInline
from documents.inlines.required import DocumentRequiredInline
from documents.models import DocumentProxy, MainDocument, RequiredDocument

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

    def test_get_inlines_with_instances_and_documents_not_in_get(self):
        # Create instances of MainDocument and RequiredDocument for the mother
        MainDocument.objects.create(mother=self.mother, title='PASSPORT', file='testfile1.txt')
        RequiredDocument.objects.create(mother=self.mother, title='BANK_ACCOUNT', file='testfile2.txt')

        request = self.factory.get('/')
        request.user = self.staff_user
        inlines = self.admin.get_inlines(request, obj=self.mother)

        # Check that both inlines are returned since both have instances and 'documents' not in GET
        self.assertTrue(any(issubclass(inline, DocumentInline) for inline in inlines))
        self.assertTrue(any(issubclass(inline, DocumentRequiredInline) for inline in inlines))

    def test_get_inlines_without_instances_and_documents_not_in_get(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        inlines = self.admin.get_inlines(request, obj=self.mother)

        # Check that no inlines are returned since no instances exist and 'documents' not in GET
        self.assertFalse(any(issubclass(inline, DocumentInline) for inline in inlines))
        self.assertFalse(any(issubclass(inline, DocumentRequiredInline) for inline in inlines))

    def test_get_inlines_with_documents_in_get(self):
        # Create instances of MainDocument and RequiredDocument for the mother
        MainDocument.objects.create(mother=self.mother, title='PASSPORT', file='testfile1.txt')
        RequiredDocument.objects.create(mother=self.mother, title='BANK_ACCOUNT', file='testfile2.txt')

        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        inlines = self.admin.get_inlines(request, obj=self.mother)

        # Check that all inlines are returned since 'documents' is in GET
        self.assertTrue(any(issubclass(inline, DocumentInline) for inline in inlines))
        self.assertTrue(any(issubclass(inline, DocumentRequiredInline) for inline in inlines))

    def test_get_inlines_without_instances_and_documents_in_get(self):
        request = self.factory.get('/', {'documents': 'test'})
        request.user = self.staff_user
        inlines = self.admin.get_inlines(request, obj=self.mother)

        # Check that all inlines are returned even though no instances exist since 'documents' is in GET
        self.assertTrue(any(issubclass(inline, DocumentInline) for inline in inlines))
        self.assertTrue(any(issubclass(inline, DocumentRequiredInline) for inline in inlines))

