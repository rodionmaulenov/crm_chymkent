from django.test import TestCase, RequestFactory
from django.urls import reverse, resolve
from django.contrib.admin.sites import AdminSite
from documents.admin import DocumentProxyAdmin
from documents.models import DocumentProxy
from mothers.models import Mother


class TestDocumentProxyAdminURLs(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.admin = DocumentProxyAdmin(DocumentProxy, self.admin_site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')

    def test_custom_urls(self):
        # Verify that the custom URLs include the download paths
        download_main_url = reverse('admin:document_main_download', args=[1])
        download_required_url = reverse('admin:document_required_download', args=[1])

        # Check that the URLs resolve correctly
        self.assertEqual(resolve(download_main_url).view_name, 'admin:document_main_download')
        self.assertEqual(resolve(download_required_url).view_name, 'admin:document_required_download')
