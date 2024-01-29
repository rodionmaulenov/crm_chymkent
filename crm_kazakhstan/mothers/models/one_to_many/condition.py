from django.db import models


class Condition(models.Model):
    class ConditionChoices(models.TextChoices):
        CREATED = 'created', 'recently created'
        NO_BABY = 'no baby', 'has not baby'
        WROTE_IN_WHATSAPP_AND_WAITING = 'WWW', 'wrote WhatsApp, waiting the answer'
        __empty__ = '__empty__'

    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    condition = models.CharField(max_length=10, choices=ConditionChoices.choices, default=ConditionChoices.__empty__,
                                 blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    scheduled_date = models.DateField(blank=True, null=True)
    scheduled_time = models.TimeField(blank=True, null=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return ''
