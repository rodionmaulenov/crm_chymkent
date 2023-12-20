from django.db import models

from mothers.constants import MESSANGER_CHOICES


class Messanger(models.Model):
    mother = models.OneToOneField("Mother", on_delete=models.CASCADE)
    messanger = models.CharField(max_length=3, choices=MESSANGER_CHOICES, blank=True, null=True)
    in_group = models.BooleanField(default=False)
    date_add_in_group = models.DateField(auto_now_add=True)