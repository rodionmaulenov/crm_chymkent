from django.test import TestCase, RequestFactory
from django.db import models
from django.contrib import admin
from django.contrib.auth import get_user_model

from mothers.inlines import StateInline
from mothers.models import Mother, State

Mother: models
State: models

User = get_user_model()


class GetQuerysetTest(TestCase):

    def setUp(self):
        self.inline_condition = StateInline(State, admin.site)

        self.factory = RequestFactory()

        self.super_user = User.objects.create_superuser('Superuser', 'password')

    def test_first_condition_not_in_queryset(self):
        mother = Mother.objects.create(name="Test")
        State.objects.create(id=1, mother=mother, condition=State.ConditionChoices.CREATED,
                             reason='for example')
        State.objects.create(id=2, mother=mother, condition=State.ConditionChoices.NO_BABY,
                             reason='for1 example')

        request = self.factory.get('/')
        request.user = self.super_user

        get_queryset = self.inline_condition.get_queryset(request)

        self.assertEqual(len(get_queryset), 1)
        self.assertEqual(get_queryset.first().reason, 'for1 example')
