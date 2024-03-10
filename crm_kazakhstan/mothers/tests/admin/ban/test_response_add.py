from django.contrib import admin
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.db import models
from django.test import TestCase, RequestFactory

from mothers.admin import BanAdmin
from mothers.models import Ban, Mother

Mother: models
Ban: models


class ResponseAddTest(TestCase):
    def setUp(self):
        self.admin = BanAdmin(Ban, admin.site)
        self.factory = RequestFactory()

        self.sm = SessionMiddleware()
        self.mm = MessageMiddleware()

    def prepare_request(self, request):
        self.sm.process_request(request)
        self.mm.process_request(request)

    def test_redirect_after_add(self):
        request = self.factory.get('/')
        self.prepare_request(request)
        mother = Mother.objects.create(name='test')
        obj = Ban.objects.create(mother=mother, comment='some reason', banned=False)

        redirect = self.admin.response_add(request, obj)
        self.assertEqual(redirect.url, "/admin/mothers/mother/")
        self.assertEqual(redirect.status_code, 302)
