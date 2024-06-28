from django.test import TestCase
from django.urls import reverse
from django.contrib.admin.sites import AdminSite

from documents.inlines.main import MainInline
from documents.models import MainDocument, Mother


class DocumentInlineTests(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.inline = MainInline(Mother, self.admin_site)
        self.mother = Mother.objects.create(name='test')
        self.document_with_file = MainDocument.objects.create(mother=self.mother, title='PASSPORT', file='path/to/file.png')
        self.document_without_file = MainDocument.objects.create(mother=self.mother, title='PASSPORT', file='')

    def test_download_link_with_file(self):
        result = self.inline.download_link(self.document_with_file)
        expected_url = reverse('admin:document_main_download', args=[self.document_with_file.id])
        self.assertIn(expected_url, result)
        self.assertIn('<img src="/static/documents/img/Download.png" alt="Download" width="35" height="35" />', result)

    def test_download_link_without_file(self):
        result = self.inline.download_link(self.document_without_file)
        self.assertEqual(result, '-')
