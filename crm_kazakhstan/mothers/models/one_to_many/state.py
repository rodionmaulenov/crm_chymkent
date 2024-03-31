from django.db import models


class State(models.Model):
    class ConditionChoices(models.TextChoices):
        EMPTY = '', '------------'
        CREATED = 'created', 'recently created'
        WORKING = 'working', 'we are working'
        NO_BABY = 'no baby', 'has not baby'
        WROTE_IN_WHATSAPP_AND_WAITING = 'WWW', 'wrote WhatsApp, waiting the answer'

    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    condition = models.CharField(max_length=20, choices=ConditionChoices.choices, default=ConditionChoices.EMPTY,
                                 blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    created = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.mother}.state instance'
