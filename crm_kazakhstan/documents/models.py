from django.db import models
import os

from documents.services import validate_max_length
from mothers.models import Mother
import re


def clean_filepath(filename):
    # Define a regular expression pattern to match prohibited characters, including apostrophes
    prohibited_characters = r'[\\/*?:"<>|\'`]'
    # Replace prohibited characters with an empty string
    cleaned_filename = re.sub(prohibited_characters, '', filename)
    return cleaned_filename


def directory_path(instance, filename):
    return f'{clean_filepath(instance.mother.name)}/{filename}'


def construct_filename(model):
    if model.file and not model.pk:
        extension = os.path.splitext(model.file.name)[1]
        model.file.name = f'{model.title.title()}{extension}'


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
        BANK_ACCOUNT = 'BANK ACCOUNT', 'Bank account'
        TRANSFER_AGREEMENT = 'TRANSFER AGREEMENT', 'Transfer agreement'

    mother = models.ForeignKey(Mother, on_delete=models.CASCADE, related_name='main_document')
    title = models.CharField(max_length=25, choices=MainDocumentChoice.choices)
    note = models.TextField(validators=[validate_max_length], blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=directory_path)

    def save(self, *args, **kwargs):
        construct_filename(self)
        super().save(*args, **kwargs)

    def __str__(self):
        # if self is None must return '' because if add new document from inline without '' the error raise
        return str(self.title).title() if self.title else ''


class AdditionalDocument(models.Model):
    mother = models.ForeignKey(Mother, on_delete=models.CASCADE, related_name='additional_document')
    title = models.CharField(max_length=50)
    note = models.TextField(validators=[validate_max_length], blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=directory_path)

    def __str__(self):
        # if self is None must return '' because if add new document from inline without '' the error raise
        return str(self.title).title() if self.title else ''

    def save(self, *args, **kwargs):
        construct_filename(self)
        super().save(*args, **kwargs)


class Document(Mother):
    class Meta:
        verbose_name = 'document'
        verbose_name_plural = 'documents'
        proxy = True
