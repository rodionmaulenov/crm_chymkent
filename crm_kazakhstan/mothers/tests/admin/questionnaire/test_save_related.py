from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.forms.models import inlineformset_factory
from mothers.admin import QuestionnaireAdmin
from mothers.models import Mother, ScheduledEvent
from django.contrib.admin.sites import AdminSite
import pytz

User = get_user_model()


class SaveRelatedTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Set up a user and request
        self.user = User.objects.create_user(username='testuser', password='12345', timezone='Europe/Kiev')

        # Create a Mother instance
        self.mother = Mother.objects.create(name='Test Mother')

        # Create the admin instance
        self.admin = QuestionnaireAdmin(Mother, AdminSite())

    def test_save_related_converts_to_utc(self):
        # Create timezone-aware ScheduledEvent instance
        local_time = timezone.datetime(2024, 7, 11, 15, 0, 0)
        kiev_tz = pytz.timezone('Europe/Kiev')
        local_time = timezone.make_aware(local_time, kiev_tz)

        # Create the form data for the inline
        form_data = {
            'scheduledevent_set-TOTAL_FORMS': '1',
            'scheduledevent_set-INITIAL_FORMS': '0',
            'scheduledevent_set-MIN_NUM_FORMS': '0',
            'scheduledevent_set-MAX_NUM_FORMS': '1000',
            'scheduledevent_set-0-scheduled_time': local_time.strftime('%Y-%m-%d %H:%M:%S%z'),
            'scheduledevent_set-0-note': 'Test Note',
            'scheduledevent_set-0-mother': self.mother.pk,
            'scheduledevent_set-0-is_completed': False,
            'scheduledevent_set-0-id': ''
        }

        # Ensure the form data includes all necessary management form fields
        formset_class = inlineformset_factory(Mother, ScheduledEvent,
                                              fields=('scheduled_time', 'note', 'mother', 'is_completed'), extra=1)
        formset = formset_class(data=form_data, instance=self.mother, prefix='scheduledevent_set')

        # Simulate request
        request = self.factory.post('/')
        request.user = self.user

        # Ensure formset is valid and print errors if not
        if not formset.is_valid():
            print(formset.errors)
            print(formset.non_form_errors())

        self.assertTrue(formset.is_valid())

        # Save the related objects
        self.admin.save_related(request, formset.forms[0], [formset], change=False)

        # Retrieve the saved ScheduledEvent
        saved_event = ScheduledEvent.objects.get(mother=self.mother)

        # Verify that the scheduled_time has been converted to UTC
        expected_utc_time = local_time.astimezone(pytz.utc)
        self.assertEqual(saved_event.scheduled_time, expected_utc_time)


