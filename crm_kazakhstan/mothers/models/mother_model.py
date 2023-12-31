from django.db import models
from django.utils import timezone


class Mother(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    number = models.CharField(max_length=100, blank=True, null=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    residence = models.CharField(max_length=100, blank=True, null=True)
    height_and_weight = models.CharField(max_length=100, blank=True, null=True)
    bad_habits = models.CharField(max_length=100, blank=True, null=True)
    caesarean = models.CharField(max_length=100, blank=True, null=True)
    children_age = models.CharField(max_length=100, blank=True, null=True)
    age = models.CharField(max_length=100, blank=True, null=True)
    citizenship = models.CharField(max_length=100, blank=True, null=True)
    blood = models.CharField(max_length=100, blank=True, null=True)
    maried = models.CharField(max_length=100, blank=True, null=True)
    date_create = models.DateTimeField(default=timezone.now)

    class Meta:
        permissions = [
            ('to_manager_on_primary_stage', 'Can do all without actions on primary stage'),
            ('action_first_visit', 'transfer mothers to the first visit'),
            ('move_to_ban', 'Can banned mother instances'),
            ('return_from_ban', 'Can return mothers instance from ban'),
            ('to_manager_on_first_stage', 'Can do all without actions  on first stage'),
            ('action_on_primary_stage', 'Return mother on primary stage'),
        ]

    def __str__(self):
        return self.name or "Unnamed Mother"
