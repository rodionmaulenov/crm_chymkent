from django.db import models

from mothers.models import Mother


class Document(models.Model):
    class DocumentTitleBase(models.TextChoices):
        PASSPORT = 'PASSPORT', 'Passport'
        PSYCHOTHERAPIST = "PSYCHOTHERAPIST", "Psychotherapist"

    class DocumentChoices(models.TextChoices):
        MAIN_DOCS = 'MAIN DOCS', 'Main documents'
        ACQUIRE_DOCS = 'ACQUIRE DOCS', 'Acquire documents'
        ADDITIONAL_DOCS = 'ADDITIONAL DOCS', 'Additional documents'

    mother = models.ForeignKey(Mother, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, choices=DocumentTitleBase.choices)
    document_kind = models.CharField(max_length=15, choices=DocumentChoices.choices)
    note = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField()

    def __str__(self):
        return str(self.title).title()


class DocumentProxy(Mother):
    class Meta:
        verbose_name = 'document'
        verbose_name_plural = 'documents'
        proxy = True
