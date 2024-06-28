from django.test import TestCase, RequestFactory
from django.http import Http404, FileResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from documents.admin import DocumentProxyAdmin
from documents.models import MainDocument, Document
from mothers.models import Mother

User = get_user_model()


class TestDocumentProxyAdminDownload(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.admin = DocumentProxyAdmin(Document, self.admin_site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')
        self.staff_user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')
        self.client.login(username='admin', password='admin')

        # Create a test document
        self.test_document = MainDocument.objects.create(
            mother=self.mother,
            title='PASSPORT',
            file=SimpleUploadedFile('testfile.txt', b'This is a test file')
        )

    def test_download_file_success(self):
        request = RequestFactory().get('/')
        response = self.admin.download_file(request, document_id=self.test_document.id)
        self.assertTrue(isinstance(response, FileResponse))

    def test_download_file_not_found(self):
        # Simulate a request to download a non-existent document
        with self.assertRaises(Http404):
            request = RequestFactory().get('/')
            self.admin.download_file(request, document_id=999)
