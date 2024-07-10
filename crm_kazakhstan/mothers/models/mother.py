from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Mother(models.Model):
    class BloodChoice(models.TextChoices):
        FIRST_POSITIVE = 'FIRST_POSITIVE', '(I)+'
        SECOND_POSITIVE = 'SECOND_POSITIVE', '(II)+'
        THIRD_POSITIVE = 'THIRD_POSITIVE', '(III)+'
        FORTH_POSITIVE = 'FORTH_POSITIVE', '(IV)+'
        FIRST_NEGATIVE = 'FIRST_NEGATIVE', '(I)-'
        SECOND_NEGATIVE = 'SECOND_NEGATIVE', '(II)-'
        THIRD_NEGATIVE = 'THIRD_NEGATIVE', '(III)-'
        FORTH_NEGATIVE = 'FORTH_NEGATIVE', '(IV)-'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    name = models.CharField(max_length=100)
    age = models.SmallIntegerField(validators=[MinValueValidator(18), MaxValueValidator(45)], blank=True, null=True)
    residence = models.CharField(max_length=100, blank=True, null=True)
    height = models.CharField(max_length=100, blank=True, null=True)
    weight = models.CharField(max_length=100, blank=True, null=True)
    caesarean = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(2)], blank=True, null=True)
    children = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], blank=True, null=True)
    blood = models.CharField(max_length=15, choices=BloodChoice.choices, default=BloodChoice.UNKNOWN)
    maried = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        # if self is None must return '' because if add new document from inline without '' the error raise
        return self.name if self.name else ''

    @property
    def has_related_documents(self):
        return self.main_document.exists() or self.additional_document.exists()

    @property
    def plan(self):
        return self.planned_set.filter(finished=False)

    @property
    def state(self):
        return self.state_set.filter(finished=False)

    @property
    def ban(self):
        return self.ban_set.filter(banned=False)


class Questionnaire(Mother):
    class Meta:
        proxy = True
        verbose_name = 'Questionnaire'
        verbose_name_plural = 'Questionnaires'
