from django.contrib.auth.models import AbstractUser
from timezone_field import TimeZoneField

from django.db import models


class CustomUser(AbstractUser):
    class StageChoices(models.TextChoices):
        TRASH = 'Trash', 'trash'
        BAN = 'Ban', 'ban'
        PRIMARY = 'Primary', 'initial stage'
        FIRST_VISIT = 'First Visit', 'first visit'
        __empty__ = "-----"
    timezone = TimeZoneField(default='UTC')
    stage = models.CharField(max_length=15, choices=StageChoices.choices, null=True, blank=True)

    def __str__(self):
        return self.username
