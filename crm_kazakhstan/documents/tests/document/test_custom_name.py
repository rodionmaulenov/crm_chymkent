from django.test import TestCase
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from documents.admin import DocumentProxyAdmin
from documents.models import Mother


class DocumentProxyAdminTest(TestCase):
    def setUp(self):
        # Create a Mother instance without related documents
        self.mother_without_docs = Mother.objects.create(name="Mother Without Docs")

        # Create a Mother instance with related documents
        self.mother_with_docs = Mother.objects.create(name="Mother With Docs")
        self.mother_with_docs.main_document.create(title='Passport', note='Test Note')

        # Create an instance of the admin class to test
        self.admin = DocumentProxyAdmin(Mother, admin.site)

    def test_custom_name_with_related_docs(self):
        # Test the method with a Mother instance that has related documents
        result = self.admin.custom_name(self.mother_with_docs)
        expected_url = reverse('admin:documents_document_change', args=[self.mother_with_docs.pk])
        expected_result = format_html(
            '<span class="hidden-data" data-related-docs="True"></span><a href="{}">Mother With Docs</a>',
            expected_url
        )
        self.assertEqual(result, expected_result)

    def test_custom_name_without_related_docs(self):
        # Test the method with a Mother instance that does not have related documents
        result = self.admin.custom_name(self.mother_without_docs)
        expected_result = format_html(
            '<span class="hidden-data" data-related-docs="False"></span>Mother Without Docs'
        )
        self.assertEqual(result, expected_result)
