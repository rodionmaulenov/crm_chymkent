from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from documents.inlines.main import DocumentInline
from documents.models import MainDocument, Mother

User = get_user_model()


class DocumentInlineTests(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.inline = DocumentInline(MainDocument, self.admin_site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')
        self.staff_user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')

    def test_get_fields_with_documents_in_query(self):
        request = self.factory.get('/admin/documents/?documents=main')
        request.user = self.staff_user
        fields = self.inline.get_fields(request, obj=self.mother)
        expected_fields = ('mother', 'title', 'file', 'note')
        self.assertEqual(fields, expected_fields)

    def test_get_fields_without_documents_in_query(self):
        request = self.factory.get('/admin/documents/')
        request.user = self.staff_user
        fields = self.inline.get_fields(request, obj=self.mother)
        expected_fields = ('get_html_photo', 'file', 'note', 'created', 'download_link')
        self.assertEqual(fields, expected_fields)


