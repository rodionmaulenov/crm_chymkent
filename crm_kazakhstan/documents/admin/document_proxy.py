from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect, FileResponse, Http404
from django.db import models
from django.urls import path, reverse

from documents.filters import OnWhatStageFilter
from documents.inlines.required import DocumentRequiredInline
from documents.inlines.main import DocumentInline
from documents.models import DocumentProxy, MainDocument, RequiredDocument
from documents.services.documnet import ProgressBarADDMain, ProgressBarADDRequired

from mothers.admin import MotherAdmin
from mothers.models import Mother, Stage
from mothers.services.mother import get_model_objects
from mothers.services.mother_classes.permissions import PermissionCheckerFactory

Mother: models

mother_admin = MotherAdmin(Mother, admin.site)


@admin.register(DocumentProxy)
class DocumentProxyAdmin(admin.ModelAdmin):
    list_per_page = 10
    ordering = ('-created',)
    list_filter = ('created', OnWhatStageFilter)
    list_display_links = ('name',)
    fieldsets = [
        (
            None,
            {
                "fields": ['name', 'age', 'number', 'program', 'blood', 'maried', 'citizenship', 'residence',
                           'height_and_weight', 'caesarean', 'children_age', 'bad_habits'],

                'description': 'Client personal data',
            },
        )
    ]
    list_display = ('id', 'name', 'add_main_docs', 'add_require_docs')
    inlines = [DocumentInline, DocumentRequiredInline]

    class Media:
        css = {
            'all': ('documents/css/add_butt.css',
                    'documents/css/increase_image_scale.css',)
        }
        js = ('documents/js/hide_history_link.js',
              'documents/js/hide_p_element.js',
              'documents/js/add_new_bottom.js',)

    def get_list_filter(self, request):
        if request.user.has_perm('documents.view_documentproxy'):
            return super().get_list_filter(request)
        return ('created',)

    def get_inlines(self, request, obj):
        # When an inline has one or more instances and then return these inlines
        # Cases when read
        if 'documents' not in request.GET:
            inlines = super().get_inlines(request, obj)
            filtered_inlines = [
                inline for inline in inlines
                if inline.model.objects.filter(mother=obj).exists()
            ]
            return filtered_inlines
        return super().get_inlines(request, obj)

    def get_list_display(self, request):
        # choose display fields based on user stage
        if request.user.stage == Stage.StageChoices.PRIMARY:
            return 'id', 'name', 'add_main_docs'
        # other stage see all documents
        return super().get_list_display(request)

    def get_actions(self, request):
        if request.user.has_perm('documents.view_documentproxy'):
            return super().get_actions(request)
        return {}

    def has_module_permission(self, request) -> bool:
        """
        With base permission 'view_documentproxy' user has full access for module level.
        In other cases, only if the user was assigned mother instances when they were created.
        """
        view_documentproxy = super().has_module_permission(request)
        class_name = 'ModuleLevel'
        permission_checker = PermissionCheckerFactory.get_checker(mother_admin, request, class_name)
        if request.user.is_authenticated:
            has_perm = permission_checker.has_permission(view_documentproxy)
        else:
            has_perm = False

        return has_perm

    def get_queryset(self, request: HttpRequest):
        # add functionality when empty queryset redirect on main page
        """
        A user with base permissions has access to all instances.
        A user who is assigned custom permission to access an object receives only those objects.
        """
        self.request = request
        user = request.user
        prefetched_list = ('state_set', 'planned_set', 'ban_set', 'stage_set', 'maindocument_set')
        queryset = Mother.objects.prefetch_related(*prefetched_list)

        if user.has_module_perms(self.opts.app_label):
            return queryset

        queryset = get_model_objects(mother_admin, request).prefetch_related(*prefetched_list)
        return queryset

    def has_view_permission(self, request: HttpRequest, mother: Mother = None):
        """
        With base permission 'view_mother' user has full access for list and object level.
        In other cases, only if the user was assigned mother instances when they were created.
        """
        class_name = 'ObjectListLevel'
        permission_checker = PermissionCheckerFactory.get_checker(mother_admin, request, class_name, 'view')
        has_perm = permission_checker.has_permission(obj=mother)
        return has_perm

    def has_change_permission(self, request, mother=None):
        """
        With base permission 'change_mother' user has full access for list and object level.
        In other cases, only if the user was assigned mother instances when they were created.
        """
        if 'documents' in request.GET:
            change_documentproxy = super().has_change_permission(request)
            class_name = 'ModuleLevel'
            permission_checker = PermissionCheckerFactory.get_checker(mother_admin, request, class_name)
            has_perm = permission_checker.has_permission(change_documentproxy)
            return has_perm
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # new button add in case when user change or add new documents
        if request.GET:
            extra_context['custom_buttons_template'] = 'admin/documents/documentproxy/custom_buttons.html'
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def response_change(self, request, obj):
        """
        Customizes the change URL and retains the default messages.
        """
        response = super().response_change(request, obj)
        if isinstance(response, HttpResponseRedirect):
            if "_save" in request.POST:
                return response
            elif "_continue" in request.POST:
                response['Location'] = request.get_full_path()
            elif "_obj_page" in request.POST:
                custom_url = reverse('admin:documents_documentproxy_change', args=(obj.id, ))
                return HttpResponseRedirect(custom_url)
        return response

    @admin.display(description='Main Docs')
    def add_main_docs(self, obj: Mother) -> str:
        """
        Add new document with progress bar.
        """
        # generates add or chane path with params from previous page and constant mother param
        # redirect on mother DocumentsInline page
        progress_bar_add_change = ProgressBarADDMain(self.request, obj)
        return progress_bar_add_change.execute()

    @admin.display(description='Acquired Docs')
    def add_require_docs(self, obj: Mother) -> str:
        """
        Add new document with progress bar.
        """
        # generates add or chane path with params from previous page and constant mother param
        # redirect on mother DocumentsInline page
        progress_bar_add_change = ProgressBarADDRequired(self.request, obj)
        return progress_bar_add_change.execute()

    def get_inline_instances(self, request, obj=None):
        """Assign custom names for inlines."""
        inline_instances = super().get_inline_instances(request, obj)
        for inline in inline_instances:
            if isinstance(inline, DocumentInline):
                inline.verbose_name = 'Main Document'
                inline.verbose_name_plural = 'Main Documents'
            elif isinstance(inline, DocumentRequiredInline):
                inline.verbose_name = 'Required Document'
                inline.verbose_name_plural = 'Required Documents'
        return inline_instances

    def get_urls(self):
        """
        Extend the default URL patterns with custom download URLs for main and required documents.
        """
        urls = super().get_urls()
        custom_urls = [
            path('download_main/<int:document_id>/', self.admin_site.admin_view(self.download_file),
                 name='document_main_download'),
            path('download_required/<int:document_id>/', self.admin_site.admin_view(self.download_required_file),
                 name='document_required_download'),
        ]
        return custom_urls + urls

    @staticmethod
    def download_file(request, document_id):
        """
        Handle file download for a given document ID.
        """
        try:
            document = MainDocument.objects.get(id=document_id)
            response = FileResponse(document.file.open(), as_attachment=True, filename=document.file.name)
            return response
        except MainDocument.DoesNotExist:
            raise Http404("Document does not exist")

    @staticmethod
    def download_required_file(request, document_id):
        """
        Handle file download for a given required document ID.
        """
        try:
            document = RequiredDocument.objects.get(id=document_id)
            response = FileResponse(document.file.open(), as_attachment=True, filename=document.file.name)
            return response
        except RequiredDocument.DoesNotExist:
            raise Http404("Document does not exist")
