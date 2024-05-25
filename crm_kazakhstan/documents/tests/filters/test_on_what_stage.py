from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from documents.admin import DocumentProxyAdmin
from documents.filters import OnWhatStageFilter
from documents.models import DocumentProxy
from mothers.models import Mother, Stage

User = get_user_model()


class OnWhatStageFilterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mother1 = Mother.objects.create(name='Mother1')
        self.mother2 = Mother.objects.create(name='Mother2')

        Stage.objects.create(mother=self.mother1, stage=Stage.StageChoices.PRIMARY, finished=False)
        Stage.objects.create(mother=self.mother2, stage=Stage.StageChoices.FIRST_VISIT, finished=False)

        self.document_admin = DocumentProxyAdmin(DocumentProxy, admin.site)
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

    def test_primary_stage_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser
        my_filter = OnWhatStageFilter(request, {'stage': 'primary_stage'}, Mother, self.document_admin)

        queryset = my_filter.queryset(request, self.document_admin.get_queryset(request))
        self.assertIn(self.mother1, queryset)
        self.assertNotIn(self.mother2, queryset)

    def test_first_visit_stage_filter(self):
        request = self.factory.get('/')
        request.user = self.superuser
        my_filter = OnWhatStageFilter(request, {'stage': 'first_visit_stage'}, Mother, self.document_admin)

        queryset = my_filter.queryset(request, self.document_admin.get_queryset(request))
        self.assertIn(self.mother2, queryset)
        self.assertNotIn(self.mother1, queryset)
