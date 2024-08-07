import logging
from django.contrib import admin
from mothers.tasks import send_telegram_message
from documents.models import MainDocument
from mothers.forms import LaboratoryAdminForm
from mothers.models.mother import Laboratory, LaboratoryFile
from django.utils import timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@admin.register(Laboratory)
class LaboratoryAdmin(admin.ModelAdmin):
    form = LaboratoryAdminForm
    actions = ['delete_selected']
    fieldsets = [
        (
            None,
            {
                "fields": [
                    'mother',
                    'passport_file',
                    'description', 'scheduled_time', 'analysis_types', 'is_completed'
                ],
            },
        ),
    ]
    list_display = ('mother', 'scheduled_time', 'is_completed')
    filter_horizontal = ('analysis_types',)

    def has_module_permission(self, request):
        return False

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if obj.scheduled_time == timezone.now():
                return False
        return True

    def get_form(self, request, obj=None, **kwargs):
        # Pass the request to the form class
        form_class = super().get_form(request, obj, **kwargs)

        class FormWithRequest(form_class):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return form_class(*args, **kwargs)

        return FormWithRequest

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)  # Save the form but don't commit yet
        instance.save()
        form.save_m2m()  # Ensure many-to-many relationships are saved
        selected_analysis_types = form.cleaned_data.get('analysis_types')

        # Extract the IDs of the selected analysis types
        selected_analysis_type_ids = list(selected_analysis_types.values_list('id', flat=True))

        # Save the passport file if it was uploaded
        passport_file = form.cleaned_data.get('passport_file')
        if passport_file:
            # Check if the passport file is new
            existing_passport = instance.mother.main_document.filter(
                title=MainDocument.MainDocumentChoice.PASSPORT
            ).first()

            if not existing_passport or existing_passport.file != passport_file:
                if existing_passport:
                    existing_passport.delete()
                # If there's no existing passport or the file has changed, save the new file
                MainDocument.objects.create(
                    mother=instance.mother,
                    title=MainDocument.MainDocumentChoice.PASSPORT,
                    file=passport_file
                )

        if change:
            # Retrieve current analysis types for the instance
            current_analysis_types = set(instance.analysis_types.all())
            selected_analysis_types_set = set(selected_analysis_types)

            # Analysis types to be added and removed
            analysis_types_to_add = selected_analysis_types_set - current_analysis_types
            analysis_types_to_remove = current_analysis_types - selected_analysis_types_set

            # Add new LaboratoryFile instances
            for analysis_type in analysis_types_to_add:
                LaboratoryFile.objects.create(
                    laboratory=instance,
                    analysis_type=analysis_type
                )

            # Remove LaboratoryFile instances that are no longer selected and no file have
            LaboratoryFile.objects.filter(
                laboratory=instance,
                analysis_type__in=analysis_types_to_remove,
                file__isnull=False
            ).delete()

        else:
            # Handle the initial creation case
            if selected_analysis_types:
                LaboratoryFile.objects.filter(laboratory=instance).delete()
                for analysis_type in selected_analysis_types:
                    LaboratoryFile.objects.create(
                        laboratory=instance,
                        analysis_type=analysis_type
                    )
        user_id = request.user.id
        # Trigger the Celery task
        send_telegram_message.delay('-1002171039112', instance.id, selected_analysis_type_ids, user_id)

