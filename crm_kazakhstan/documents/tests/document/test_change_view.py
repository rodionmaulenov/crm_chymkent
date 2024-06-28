from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from documents.admin import DocumentProxyAdmin
from documents.models import Document

from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

User = get_user_model()
Mother: models


class HasViewPermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.mother_admin = MotherAdmin(Mother, self.site)
        self.document_admin = DocumentProxyAdmin(Document, self.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='Mother 1')
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_change_view_with_get_request(self):
        # Create a GET request
        url = reverse('admin:documents_document_change', args=[self.mother.id])
        request = self.factory.get(url, data={'test': 'data'})
        request.user = self.superuser

        # Get the response
        response = self.document_admin.change_view(request, str(self.mother.id))

        # Check that the custom_buttons_template is in the context
        self.assertIn('custom_buttons_template', response.context_data)

    def test_change_view_without_get_request(self):
        # Create a GET request
        url = reverse('admin:documents_document_change', args=[self.mother.id])
        request = self.factory.get(url)
        request.user = self.superuser

        # Get the response
        response = self.document_admin.change_view(request, str(self.mother.id))

        # Check that the custom_buttons_template is in the context
        self.assertNotIn('custom_buttons_template', response.context_data)
