from django.db import models

from mothers.constants import CONDITION_CHOICES


class Condition(models.Model):
    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    condition = models.CharField(max_length=3, choices=CONDITION_CHOICES)
    reason = models.TextField(blank=True, null=True)
    scheduled_date = models.DateField(blank=True, null=True)
    scheduled_time = models.TimeField(blank=True, null=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return ''
