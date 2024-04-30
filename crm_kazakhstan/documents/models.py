from django.db import models

from mothers.models import Mother


class Document(models.Model):
    class KindDocumentChoices(models.TextChoices):
        MAIN = 'MAIN', 'Main'
        ACQUIRED_FOR_PROGRAM = 'ACQUIRED FOR PROGRAM', 'Acquired for program'
        ADDITIONAL = 'ADDITIONAL', 'Additional'

    class MainDocumentChoice(models.TextChoices):
        PASSPORT = 'PASSPORT', 'Passport'
        INTERNATIONAL_PASSPORT = 'INTERNATIONAL PASSPORT', 'International passport'
        NO_CRIMINAL_RECORD = 'NO_CRIMINAL_RECORD', 'No criminal record'
        NARCOLOGIST = 'NARCOLOGIST', 'Narcologist'
        PSYCHOTHERAPIST = 'PSYCHOTHERAPIST', 'Psychotherapist'
        MOTHERS_METRIC = 'MOTHERS METRIC', 'Mother\'s metric'
        CHILD_METRIC = 'CHILD METRIC', 'Child metric'

    mother = models.ForeignKey(Mother, on_delete=models.CASCADE)
    kind = models.CharField(max_length=25, choices=KindDocumentChoices.choices)
    title = models.CharField(max_length=25, choices=MainDocumentChoice.choices)
    note = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField()

    def __str__(self):
        return str(self.title).title()


class DocumentProxy(Mother):
    class Meta:
        verbose_name = 'document_proxy'
        verbose_name_plural = 'documents_proxy'
        proxy = True
