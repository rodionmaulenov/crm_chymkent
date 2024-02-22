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
        for_compare = ('id', 'when_created', 'name', 'number', 'age', 'blood', 'create_condition_link',
                       'create_condition_datetime')
        self.assertEqual(list_display, for_compare)

    def test_specific_list_for_planned_time(self):
        url = '/admin/mothers/mother/'
        query_parameters = {'planned_time': 'datetime'}
        url_with_query_param = f'{url}?{urlencode(query_parameters)}'
        request = self.factory.get(url_with_query_param)
        request.user = self.superuser

        list_display = self.admin.get_list_display(request)
        for_compare = ('id', 'name', 'number', 'age', 'blood', 'reason',
                       'create_condition_link', 'create_condition_datetime')

        self.assertEqual(list_display, for_compare)

    def test_specific_list_for_empty_state(self):
        url = '/admin/mothers/mother/'
        query_parameters = {'empty_state': 'empty_condition'}
        url_with_query_param = f'{url}?{urlencode(query_parameters)}'
        request = self.factory.get(url_with_query_param)
        request.user = self.superuser

        list_display = self.admin.get_list_display(request)
        for_compare = ('id', 'name', 'number', 'age', 'blood', 'reason',
                       'create_condition_link', 'create_condition_datetime')

        self.assertEqual(list_display, for_compare)

    def test_specific_list_for_recently_created(self):
        url = '/admin/mothers/mother/'
        query_parameters = {'recently_created': 'status_created'}
        url_with_query_param = f'{url}?{urlencode(query_parameters)}'
        request = self.factory.get(url_with_query_param)
        request.user = self.superuser

        list_display = self.admin.get_list_display(request)
        for_compare = ('id', 'name', 'number', 'age', 'blood', 'reason','create_condition_link')

        self.assertEqual(list_display, for_compare)
