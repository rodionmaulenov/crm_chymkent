from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.admin import DocumentAdmin
from documents.models import Document

from mothers.models import Mother

Mother: models
Document: models


class GetReadOnlyFieldsMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = DocumentAdmin(Document, admin.site)

    def test_get_readonly_fields_when_add(self):
        request = self.factory.get('/')
        readonly_fields = self.admin.get_readonly_fields(request)
        self.assertEqual(readonly_fields, ())

    def test_get_readonly_fields_when_change(self):
        mother = Mother.objects.create(name='Test Mother')
        mock_file = SimpleUploadedFile('test.txt', b'This is a test file', content_type='text/plain')
        document = Document.objects.create(mother=mother, file=mock_file, note='some', title='some')

        request = self.factory.get('/')
        readonly_fields = self.admin.get_readonly_fields(request, document)
        self.assertEqual(readonly_fields, self.admin.readonly_fields)
