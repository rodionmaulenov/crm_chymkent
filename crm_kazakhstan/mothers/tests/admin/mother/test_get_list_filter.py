from django.test import TestCase, RequestFactory
from django.contrib import admin

from mothers.admin import MotherAdmin
from mothers.filters import DateFilter, CreatedStatusFilter, ConditionDateFilter, PlannedTimeFilter, EmptyConditionFilter
from mothers.models import Mother


class GetListFilterTest(TestCase):
    def setUp(self):
        self.admin = MotherAdmin(Mother, admin.site)
        self.factory = RequestFactory()

    def test_request_param_recently_created(self):
        request = self.factory.get('admin/mothers/mother/?recently_created=status_created')
        list_filters = self.admin.get_list_filter(request)
        self.assertEqual(list_filters[0], DateFilter)
        self.assertEqual(list_filters[1], CreatedStatusFilter)

    def test_request_param_planned_time(self):
        request = self.factory.get('admin/mothers/mother/?planned_time=datetime')
        list_filters = self.admin.get_list_filter(request)
        self.assertEqual(list_filters[0], ConditionDateFilter)
        self.assertEqual(list_filters[1], PlannedTimeFilter)

    def test_request_param_empty_state(self):
        request = self.factory.get('admin/mothers/mother/?empty_state=empty_condition')
        list_filters = self.admin.get_list_filter(request)
        self.assertEqual(list_filters[0], ConditionDateFilter)
        self.assertEqual(list_filters[1], EmptyConditionFilter)

