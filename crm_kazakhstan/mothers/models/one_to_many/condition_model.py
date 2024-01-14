from django.contrib.auth.models import Group
from django.db import models
from guardian.shortcuts import assign_perm


class Condition(models.Model):
    class ConditionChoices(models.TextChoices):
        CREATED = 'created', 'recently created'
        NO_BABY = 'no baby', 'has not baby'
        WROTE_IN_WHATSAPP_AND_WAITING = 'WWW', 'wrote WhatsApp, waiting the answer'

    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    condition = models.CharField(max_length=10, choices=ConditionChoices.choices, default=ConditionChoices.CREATED)
    reason = models.TextField(blank=True, null=True)
    scheduled_date = models.DateField(blank=True, null=True)
    scheduled_time = models.TimeField(blank=True, null=True)
    finished = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Determine whether the object is being created or updated
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            # Get or create the group
            group, created = Group.objects.get_or_create(name='primary_stage')

            # Assign permission for each instance of Condition
            assign_perm('view_condition', group, self)
            assign_perm('change_condition', group, self)

    def __str__(self):
        return self.get_condition_display()
