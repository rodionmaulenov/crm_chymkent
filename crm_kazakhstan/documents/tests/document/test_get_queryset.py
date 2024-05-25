from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from documents.admin import DocumentAdmin
from documents.models import MainDocument

User = get_user_model()


class GetQuerySetTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = DocumentAdmin(MainDocument, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

    def test_queryset_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser

        self.assertTrue(not hasattr(self.admin, 'request'))
        self.admin.get_queryset(request)
        self.assertTrue(hasattr(self.admin, 'request'))
