from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.admin.sites import AdminSite

from mothers.admin import QuestionnaireAdmin
from mothers.filters.questionnaire import IsNewFilter
from mothers.models import Mother, ScheduledEvent

User = get_user_model()


class IsNewFilterTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.mother_new = Mother.objects.create(name='New Mother')
        self.mother_old = Mother.objects.create(name='Old Mother')

        # Create scheduled events for the old mother
        ScheduledEvent.objects.create(
            mother=self.mother_old,
            note='Event',
            scheduled_time=timezone.now(),
            is_completed=False
        )

        self.admin_site = AdminSite()
        self.questionnaire_admin = QuestionnaireAdmin(Mother, self.admin_site)

    def test_filter_lookups(self):
        request = self.factory.get('/')
        request.user = self.user
        filter_ = IsNewFilter(request, {}, Mother, self.questionnaire_admin)

        lookups = filter_.lookups(request, self.questionnaire_admin)
        expected_lookups = [('new', 'New'), ('old', 'Old')]
        self.assertEqual(expected_lookups, lookups)

    def test_filter_old_mothers(self):
        request = self.factory.get('/')
        request.user = self.user
        filter_ = IsNewFilter(request, {'new_or_old': 'old'}, Mother, self.questionnaire_admin)

        queryset = filter_.queryset(request, Mother.objects.all())
        self.assertEqual(queryset.first(), Mother.objects.filter(name='Old Mother').first())

    def test_filter_new_mothers(self):
        request = self.factory.get('/')
        request.user = self.user
        filter_ = IsNewFilter(request, {'new_or_old': 'new'}, Mother, self.questionnaire_admin)

        queryset = filter_.queryset(request, Mother.objects.all())
        self.assertEqual(queryset.first(), Mother.objects.filter(name='New Mother').first())
