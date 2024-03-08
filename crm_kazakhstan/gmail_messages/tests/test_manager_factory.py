from django.test import TestCase
from django.db import models
from django.contrib.auth import get_user_model

from gmail_messages.models import CustomUser
from gmail_messages.services.manager_factory import ManagerFactory

from mothers.models import Mother

Mother: models

User = get_user_model()


class ManagerFactoryTest(TestCase):
    def setUp(self):
        self.mother = Mother.objects.create()

    def test_manager_factory_without_user(self):
        user = User.objects.create_user(username='first_user', password='password', is_staff=True,
                                        stage=CustomUser.StageChoices.PRIMARY)
        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(['primary_stage'], self.mother)

        self.assertTrue(user.has_perm('mothers.primary_stage', self.mother))

    def test_manager_factory_with_user(self):
        user = User.objects.create_user(username='first_user', password='password', is_staff=True,
                                        stage=CustomUser.StageChoices.PRIMARY)
        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(['primary_stage'], self.mother, user)

        self.assertTrue(user.has_perm('mothers.primary_stage', self.mother))

    def test_manager_factory_different_users(self):
        User.objects.create_user(username='first_user', password='password', is_staff=True,
                                        stage=CustomUser.StageChoices.PRIMARY)
        User.objects.create_user(username='second_user', password='password', is_staff=True,
                                 stage=CustomUser.StageChoices.PRIMARY)

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(['primary_stage'], self.mother)

        with self.assertRaises(AssertionError):
            for user in User.objects.all():
                self.assertTrue(user.has_perm('mothers.primary_stage', self.mother))
