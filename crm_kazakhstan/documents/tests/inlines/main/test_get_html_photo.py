from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.html import escape
from documents.inlines.main import DocumentInline
from documents.models import MainDocument, Mother
from django.contrib.admin.sites import AdminSite


class DocumentInlineTests(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.inline = DocumentInline(Mother, self.admin_site)
        self.mother = Mother.objects.create(name='test')

    def test_get_html_photo_with_image(self):
        # Create a document with an image file
        document_with_image = MainDocument.objects.create(
            mother=self.mother,
            title='PASSPORT',
            file=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        )
        result = self.inline.get_html_photo(document_with_image)
        file_url = escape(document_with_image.file.url)
        expected_result = f"""
            <div class='image-container'>
                <img src='{file_url}' class='hoverable-image' />
            </div>
        """
        self.assertHTMLEqual(result.strip(), expected_result.strip())
    def test_get_html_photo_with_pdf(self):
        # Create a document with a PDF file
        document_with_pdf = MainDocument.objects.create(
            mother=self.mother,
            title='PASSPORT',
            file=SimpleUploadedFile(name='test_document.pdf', content=b'', content_type='application/pdf')
        )
        result = self.inline.get_html_photo(document_with_pdf)
        self.assertEqual(result, '-')

    def test_get_html_photo_without_file(self):
        # Create a document without a file
        document_without_file = MainDocument.objects.create(
            mother=self.mother,
            title='PASSPORT'
        )
        result = self.inline.get_html_photo(document_without_file)
        self.assertIsNone(result)
