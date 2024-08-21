import logging
from django.contrib import admin
from mothers.tasks import send_telegram_message
from documents.models import MainDocument
from mothers.forms import LaboratoryAdminForm
from mothers.models.mother import Laboratory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()

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
                # and delete from local storage
                if existing_passport:
                    existing_passport.delete()
                # If there's no existing passport or the file has changed, save the new file
                MainDocument.objects.create(
                    mother=instance.mother,
                    title=MainDocument.MainDocumentChoice.PASSPORT,
                    file=passport_file
                )

        user_id = request.user.id

        user = User.objects.get(id=user_id)
        # user_timezone = str(user.timezone)
        # if user_timezone == 'Asia/Tashkent':
        #     group = '-1002171039112'

        if not instance.is_completed:
            # Trigger the Celery task
            send_telegram_message.delay('-1002171039112', instance.id, selected_analysis_type_ids, user_id)

    def response_add(self, request, obj, post_url_continue=None):
        # Redirect to a specific URL after adding
        return HttpResponseRedirect(reverse('admin:mothers_questionnaire_changelist'))

    def response_change(self, request, obj):
        # Redirect to a specific URL after changing
        return HttpResponseRedirect(reverse('admin:mothers_plannedlaboratory_changelist'))



