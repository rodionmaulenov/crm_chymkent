import random
from typing import Union

from guardian.shortcuts import assign_perm
from abc import ABC, abstractmethod

from django.contrib.auth import get_user_model
from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()


class Manager(ABC):

    def assign_user(self, content_type: Union[admin.ModelAdmin, str], obj: models, user: User = None):
        """
        User is being assigned obj permission.
        """
        app_label = content_type if not isinstance(content_type, admin.ModelAdmin) \
            else content_type.model._meta.app_label

        user = self.get_user(user)
        username = user.username
        stage = self.get_stage().value
        model = obj.__class__.__name__
        codename = f'{stage}_{model}_{username}'.lower()
        name = f'{stage} {model} {username}'.lower()

        model_class = apps.get_model(app_label, model)
        content_type = ContentType.objects.get_for_model(model_class)
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type,
        )
        assign_perm(permission, user, obj)

    @staticmethod
    @abstractmethod
    def get_stage():
        pass

    def get_user(self, user: User = None):
        """
        User, if passed, otherwise users will be filtered depending on what ``stage`` they are at.
        Random choice is used for user is assigned for obj between pass from stage to stage.
        """
        if user is not None:
            if user.stage == self.get_stage().value:
                return user
        stage = self.get_stage()
        users = User.objects.filter(stage=stage)
        user = random.choice(users)
        return user
