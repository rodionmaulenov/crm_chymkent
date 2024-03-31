from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from urllib.parse import urlencode

from mothers.models import Mother
from mothers.admin import MotherAdmin

User = get_user_model()
Stage: models
Mother: models


class GetListDisplayMethodTest(TestCase):
    def setUp(self):
        self.admin = MotherAdmin(Mother, admin.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

    def test_the_default_list_display(self):
        request = self.factory.get('/')
        request.user = self.superuser

        list_display = self.admin.get_list_display(request)
        for_compare = (
            'id', 'when_created', 'name', 'number', 'age', 'blood', 'create_plan', 'create_state'
        )
        self.assertEqual(list_display, for_compare)

    def test_specific_list_for_scheduled_event(self):
        url = '/admin/mothers/mother/'
        query_parameters = {'filter_set': 'scheduled_event'}
        url_with_query_param = f'{url}?{urlencode(query_parameters)}'
        request = self.factory.get(url_with_query_param)
        request.user = self.superuser

        list_display = self.admin.get_list_display(request)
        for_compare = ('id', 'name', 'number', 'age', 'blood',
                       'create_state', 'state_datetime', 'reason')

        self.assertEqual(list_display, for_compare)

    def test_specific_list_for_planned_actions(self):
        url = '/admin/mothers/mother/'
        query_parameters = {'actions': 'planned_actions'}
        url_with_query_param = f'{url}?{urlencode(query_parameters)}'
        request = self.factory.get(url_with_query_param)
        request.user = self.superuser

        list_display = self.admin.get_list_display(request)
        for_compare = ('id', 'name', 'number', 'age', 'blood', 'create_plan')

        self.assertEqual(list_display, for_compare)

    def test_specific_list_for_state_actions(self):
        url = '/admin/mothers/mother/'
        query_parameters = {'actions': 'state_actions'}
        url_with_query_param = f'{url}?{urlencode(query_parameters)}'
        request = self.factory.get(url_with_query_param)
        request.user = self.superuser

        list_display = self.admin.get_list_display(request)
        for_compare = 'id', 'name', 'number', 'age', 'blood', 'create_state', 'reason', 'state_datetime'

        self.assertEqual(list_display, for_compare)
