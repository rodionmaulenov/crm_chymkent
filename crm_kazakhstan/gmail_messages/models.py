from django.contrib.auth.models import AbstractUser
from timezone_field import TimeZoneField

from django.db import models


class CustomUser(AbstractUser):
    class CountryChoices(models.TextChoices):
        UZBEKISTAN = 'UZBEKISTAN', 'Uzbekistan'
        KYRGYZSTAN = 'KYRGYZSTAN', 'Kyrgyzstan'

    timezone = TimeZoneField(default='UTC')
    country = models.CharField(max_length=30, choices=CountryChoices.choices, null=True, blank=True)

    def __str__(self):
        return self.username
