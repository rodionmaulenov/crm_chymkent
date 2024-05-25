from django.db import models
import os
from mothers.models import Mother


class MainDocument(models.Model):
    class MainDocumentChoice(models.TextChoices):
        PASSPORT = 'PASSPORT', 'Passport'
        INTERNATIONAL_PASSPORT = 'INTERNATIONAL PASSPORT', 'International passport'
        NO_CRIMINAL_RECORD = 'NO CRIMINAL RECORD', 'No criminal record'
        NARCOLOGIST = 'NARCOLOGIST', 'Narcologist'
        MARIED = 'MARIED', 'Maried'
        PSYCHOTHERAPIST = 'PSYCHOTHERAPIST', 'Psychotherapist'
        MOTHERS_METRIC = 'MOTHERS METRIC', 'Mother\'s metric'
        CHILD_METRIC = 'CHILD METRIC', 'Child metric'

    mother = models.ForeignKey(Mother, on_delete=models.CASCADE)
    title = models.CharField(max_length=25, choices=MainDocumentChoice.choices)
    note = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    file = models.FileField()

    def save(self, *args, **kwargs):
        if self.file and not self.pk:
            filename = os.path.splitext(self.file.name)[1]
            self.file.name = str(self.title).title() + filename
        super().save(*args, **kwargs)

    def __str__(self):
        # if self is None must return '' because if add new document from inline without '' the error raise
        return str(self.title).title() if self.title else ''


class RequiredDocument(models.Model):
    class RequiredDocumentChoice(models.TextChoices):
        BANK_ACCOUNT = 'BANK ACCOUNT', 'Bank account'
        TRANSFER_AGREEMENT = 'TRANSFER AGREEMENT', 'Transfer agreement'

    mother = models.ForeignKey(Mother, on_delete=models.CASCADE)
    title = models.CharField(max_length=25, choices=RequiredDocumentChoice.choices)
    note = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    file = models.FileField()

    def __str__(self):
        # if self is None must return '' because if add new document from inline without '' the error raise
        return str(self.title).title() if self.title else ''

    def save(self, *args, **kwargs):
        if self.file and not self.pk:
            filename = os.path.splitext(self.file.name)[1]
            self.file.name = str(self.title).title() + filename
        super().save(*args, **kwargs)


# class AdditionalDocument(Document):
#     pass


class DocumentProxy(Mother):
    class Meta:
        verbose_name = 'documentproxy'
        verbose_name_plural = 'documentsproxys'
        proxy = True
