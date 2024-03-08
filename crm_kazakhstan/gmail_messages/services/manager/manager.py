import random

from guardian.shortcuts import assign_perm
from abc import ABC, abstractmethod

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Manager(ABC):

    def assign_user(self, actions: list, obj: models, user: User = None):
        """User is assigned custom obj level ``Permission`` for specific obj and model level ``Permission`` too."""
        user = self.get_user(user)
        for action in actions:
            assign_perm(action, user, obj)

    @staticmethod
    @abstractmethod
    def get_stage():
        pass

    def get_user(self, user: User = None):
        """User, if passed, otherwise users will be filtered depending on what ``stage`` they are at."""
        if user is not None:
            if user.stage == self.get_stage().value:
                return user
        stage = self.get_stage()
        users = User.objects.filter(stage=stage)
        user = random.choice(users)
        return user
