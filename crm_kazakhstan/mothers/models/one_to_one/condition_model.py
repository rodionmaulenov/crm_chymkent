from django.db import models
from django.utils import timezone

from mothers.constants import CONDITION_CHOICES


class Condition(models.Model):
    mother = models.OneToOneField("Mother", on_delete=models.CASCADE)
    condition = models.CharField(max_length=3, choices=CONDITION_CHOICES)
    reason = models.TextField(blank=True, null=True)
    scheduled_date = models.DateField(default=timezone.now, blank=True, null=True)
    scheduled_time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return self.get_condition_display()
