from django.db import models
from django.utils import timezone

from mothers.constants import MESSANGER_CHOICES, CONDITION_CHOICES


# class Stage(models.Model):
#     ON_ANALYSIS = 'OA'
#     # DIPHERELIN = 'DPH'
#     # FIRST_VISIT_KIEV = 'FVK'
#     STAGE_CHOICES = [
#         (ON_ANALYSIS, 'On analysis'),
#         # (DIPHERELIN, 'Dipherelin'),
#         # (FIRST_VISIT_KIEV, "First visit"),
#     ]
#     mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
#     stage = models.CharField(max_length=3, choices=STAGE_CHOICES, blank=True, null=True)
#
#     def __str__(self):
#         return self.get_stage_display()

class Comment(models.Model):
    mother = models.OneToOneField("Mother", on_delete=models.CASCADE)
    description = models.TextField()
    revoked = models.BooleanField(default=False)


class Condition(models.Model):
    mother = models.OneToOneField("Mother", on_delete=models.CASCADE)
    condition = models.CharField(max_length=3, choices=CONDITION_CHOICES)
    reason = models.TextField(blank=True, null=True)
    scheduled_date = models.DateField(blank=True, null=True)
    scheduled_time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return self.get_condition_display()


class Messanger(models.Model):
    mother = models.OneToOneField("Mother", on_delete=models.CASCADE)
    messanger = models.CharField(max_length=3, choices=MESSANGER_CHOICES, blank=True, null=True)
    in_group = models.BooleanField(default=False)
    date_add_in_group = models.DateField(auto_now_add=True)


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
            ('main_manager_condition_filter_option', 'Can filter mothers by inline on their questionnaire'),
            ('revoke_mothers', 'Can revoke mothers instance'),
            ('return_mothers', 'Can return mothers instance'),
            ('can_view_first_visit_mothers', 'Can view mothers with first visit stage')
        ]

    def __str__(self):
        return self.name
