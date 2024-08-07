from mothers.models.mother import Laboratory
from django import forms
from documents.models import MainDocument
from django.forms import HiddenInput


class LaboratoryAdminForm(forms.ModelForm):
    passport_file = forms.FileField(required=True, label='Passport File')

    class Meta:
        model = Laboratory
        fields = ['mother', 'passport_file', 'description', 'scheduled_time', 'analysis_types', 'is_completed']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Retrieve the instance being edited, if available
        instance = kwargs.get('instance')
        #Check if the form is for adding a new instance
        mother_id = request.GET.get('mother')
        if instance is None:
            self.fields['mother'].initial = mother_id
            self.fields['mother'].widget = HiddenInput()

        # Check if the form is for editing an existing instance
        if instance and instance.mother:
            # Set the mother field as read-only
            self.fields['mother'].widget = HiddenInput()
            self.fields['mother'].initial = mother_id

        if instance and instance.mother:
            # Check if the mother has a passport document
            existing_passport = MainDocument.objects.filter(
                mother=instance.mother,
                title=MainDocument.MainDocumentChoice.PASSPORT
            ).first()

            if existing_passport:
                # Set a placeholder or initial for displaying the existing file name
                self.fields['passport_file'].widget.attrs['placeholder'] = existing_passport.file.name

                # Display a link to the existing file if it's not a new form
                self.fields['passport_file'].help_text = (
                    f'Existing File: <a href="{existing_passport.file.url}" target="_blank">{existing_passport.file.name}</a>'
                )

                # Make file upload optional since there's already an existing file
                self.fields['passport_file'].required = False
