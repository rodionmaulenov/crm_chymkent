from django.contrib.auth.models import AbstractUser
from timezone_field import TimeZoneField

from django.db import models

from mothers.models import Stage


class CustomUser(AbstractUser):
    timezone = TimeZoneField(default='UTC')
    stage = models.CharField(max_length=30, choices=Stage.StageChoices.choices, null=True, blank=True)

    def __str__(self):
        return self.username
