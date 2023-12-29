from datetime import datetime

from django.http import HttpRequest
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.utils import timezone
from django.db import models

from mothers.admin import MotherAdmin
from mothers.inlines import ConditionInline
from mothers.models import Mother, Condition

User = get_user_model()
Mother: models
Condition: models


class ConditionInlineButtonTest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.mother_admin = MotherAdmin(Mother, admin.site)

        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password')

    def test_formset_max_number_equal_count_of_condition_finished_True_plus_one(self):
        mother = Mother.objects.create(name='Test1 Mother')
        for _ in range(2):
            Condition.objects.create(mother=mother, finished=True,
                                     scheduled_date=datetime(2023, 12, 13, tzinfo=timezone.utc),
                                     condition='FR2'
                                     )

        request = self.request_factory.get('/')
        request.user = self.user

        formset = ConditionInline(Mother, admin.site).get_formset(request=request, obj=mother)

        # must equal sum Condition instances.finished = True and
        # not {'_changelist_filters' : ['by_date', 'by_date_and_time']}
        self.assertEqual(3, formset.max_num)

    def test_formset_max_number_when_all_condition_finished_False(self):
        mother = Mother.objects.create(name='Test2 Mother')
        for _ in range(2):
            Condition.objects.create(mother=mother, finished=False,
                                     scheduled_date=datetime(2023, 12, 13, tzinfo=timezone.utc),
                                     condition='FR2'
                                     )

        request = self.request_factory.get('/')
        request.user = self.user

        formset = ConditionInline(Mother, admin.site).get_formset(request=request, obj=mother)

        # Must equal 1 by default when all condition.finished = False
        self.assertEqual(1, formset.max_num)

    def test_formset_max_number_when_not_all_condition_finished_False(self):
        mother = Mother.objects.create(name='Test3 Mother')
        for _ in range(2):
            Condition.objects.create(mother=mother, finished=True,
                                     scheduled_date=datetime(2023, 12, 13, tzinfo=timezone.utc),
                                     condition='FR2'
                                     )
        for _ in range(2):
            Condition.objects.create(mother=mother, finished=False,
                                     scheduled_date=datetime(2023, 12, 13, tzinfo=timezone.utc),
                                     condition='FR2'
                                     )

        request = self.request_factory.get('/')
        request.user = self.user

        formset = ConditionInline(Mother, admin.site).get_formset(request=request, obj=mother)

        # Must equal sum Condition.finished = True when some condition.finished = False
        self.assertEqual(3, formset.max_num)

    def test_formset_max_number_equal_count_of_condition_finished_True_plus_one_and_not_changelist_filters(self):
        mother = Mother.objects.create(name='Test3 Mother')
        for _ in range(2):
            Condition.objects.create(mother=mother, finished=True,
                                     scheduled_date=datetime(2023, 12, 13, tzinfo=timezone.utc),
                                     condition='FR2'
                                     )

        request = HttpRequest()
        request.user = self.user
        request.GET = {'_changelist_filters': 'date_or_time=by_date_and_time'}

        formset = ConditionInline(Mother, admin.site).get_formset(request=request, obj=mother)

        # Must equal 1 because have {'_changelist_filters': 'date_or_time=by_date_and_time'} in request
        self.assertEqual(1, formset.max_num)
