from django.contrib.auth.models import AbstractUser
from timezone_field import TimeZoneField


class CustomUser(AbstractUser):
    timezone = TimeZoneField(default='UTC')

    def __str__(self):
        return self.username