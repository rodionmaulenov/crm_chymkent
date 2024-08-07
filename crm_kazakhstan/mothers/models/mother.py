import logging

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from documents.services import validate_max_length

logger = logging.getLogger('custom_logger')


class ScheduledEvent(models.Model):
    mother = models.ForeignKey("Mother", on_delete=models.CASCADE, related_name='scheduled_event')
    note = models.TextField(validators=[validate_max_length], blank=True, null=True)
    scheduled_time = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)


class LaboratoryFile(models.Model):
    laboratory = models.ForeignKey("Laboratory", on_delete=models.CASCADE, related_name='files_laboratory')
    analysis_type = models.ForeignKey("AnalysisType", on_delete=models.CASCADE, related_name='files_analysis')
    file = models.FileField(upload_to='laboratory_files/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.laboratory} - {self.analysis_type}"


class AnalysisType(models.Model):
    SEROLOGY = 'SEROLOGY'
    CYTOLOGY = 'CYTOLOGY'
    ANALYSIS_TYPE_CHOICES = [
        (SEROLOGY, 'Serology'),
        (CYTOLOGY, 'Cytology')
    ]

    name = models.CharField(max_length=20, choices=ANALYSIS_TYPE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class DoctorAnswer(models.Model):
    laboratory = models.OneToOneField('Laboratory', on_delete=models.CASCADE)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"Message {self.message_id} for Laboratory {self.laboratory_id}"


class Laboratory(models.Model):
    mother = models.ForeignKey("Mother", on_delete=models.CASCADE, related_name='laboratories')
    description = models.TextField(blank=True, null=True)
    scheduled_time = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    analysis_types = models.ManyToManyField(AnalysisType, related_name='laboratories')

    def __str__(self):
        return f"Planning a visit Laboratory for {self.mother.name}"


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

    @property
    def has_related_documents(self):
        return self.main_document.exists() or self.additional_document.exists()

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        # if self is None must return '' because if add new document from inline without '' the error raise
        return self.name if self.name else ''


class Questionnaire(Mother):
    class Meta:
        proxy = True
        verbose_name = 'Questionnaire'
        verbose_name_plural = 'Questionnaires'


class ShortPlan(Mother):
    class Meta:
        proxy = True
        verbose_name = 'Short Plan'
        verbose_name_plural = 'Short Plans'


class PlannedLaboratory(Mother):
    class Meta:
        proxy = True
        verbose_name = 'Laboratory'
        verbose_name_plural = 'Laboratories'
