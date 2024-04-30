from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.admin import DocumentAdmin
from documents.models import Document

from mothers.models import Mother

Mother: models
Document: models


class GetFieldsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = DocumentAdmin(Document, admin.site)

    def test_change_case(self):
        mother = Mother.objects.create(name='Test Mother')
        mock_file = SimpleUploadedFile('test.txt', b'This is a test file', content_type='text/plain')
        document = Document.objects.create(mother=mother, file=mock_file, note='some', title='some')

        request = self.factory.get('/')
        fields = self.admin.get_fields(request, document)

        expected_fields = ()

        self.assertEqual(fields, expected_fields)

    def test_add_case(self):
        request = self.factory.get('/')
        fields = self.admin.get_fields(request, obj=None)

        expected_fields = ('mother', 'kind', 'title', 'note', 'file')

        self.assertEqual(fields, expected_fields)
