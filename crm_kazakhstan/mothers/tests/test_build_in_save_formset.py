import datetime
import pytz

from freezegun import freeze_time

from django.utils import timezone
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.forms.models import inlineformset_factory
from django.db import models

from mothers.models import Mother, Condition
from mothers.admin import MotherAdmin

User = get_user_model()
Mother: models
Condition: models


class SaveFormsetTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_user('admin', 'admin@example.com', 'password', timezone='Europe/Kiev')
        self.mother_instance = Mother.objects.create(name='Test Mother')

        # Create an inline formset for Condition
        self.ConditionFormSet = inlineformset_factory(Mother, Condition, fields='__all__')

    @freeze_time("2023-12-20 10:15:00")
    def test_save_formset_saves_utc_aware_time(self):
        # Server's UTC time
        utc_time = timezone.now()
        # print("Server UTC time:", utc_time)

        # Convert to user's local time + 2 hours equal "2023-12-20 12:15:00"
        user_timezone = pytz.timezone(self.user.timezone)
        local_time = utc_time.astimezone(user_timezone)
        # print("User's local time:", local_time)

        request = self.factory.post('/')
        request.user = self.user

        # Simulate form data submission using user's local time
        form_data = {
            'condition-TOTAL_FORMS': '1',
            'condition-INITIAL_FORMS': '0',
            'condition-MIN_NUM_FORMS': '0',
            'condition-MAX_NUM_FORMS': '1000',
            'condition-0-mother': str(self.mother_instance.pk),
            'condition-0-condition': 'WWW',
            'condition-0-scheduled_date': '2023-12-20',
            'condition-0-scheduled_time': '12:45:00',
        }

        # Create formset instance with the form data
        formset = self.ConditionFormSet(form_data, instance=self.mother_instance)
        # Check if the formset is valid
        if formset.is_valid():
            # Call the save_formset method
            self.admin.save_formset(request, None, formset, None)

            # Retrieve the saved condition instance and verify the time
            condition = Condition.objects.first()
            if condition:
                self.assertIsNotNone(condition.scheduled_time)
                self.assertEqual(condition.scheduled_time, datetime.time(10, 45))
