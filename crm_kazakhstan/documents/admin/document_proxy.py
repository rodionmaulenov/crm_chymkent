from django.contrib import admin
from django.http import HttpResponseRedirect, FileResponse, Http404
from django.urls import path, reverse
from django.utils.html import format_html

from documents.inlines.additional import AdditionalInline
from documents.inlines.main import MainInline
from documents.models import Document, MainDocument, AdditionalDocument
#
# from gmail_messages.tasks import Stage

from mothers.admin import MotherAdmin
from mothers.models import Mother

from guardian.shortcuts import get_objects_for_user


@admin.register(Document)
class DocumentProxyAdmin(admin.ModelAdmin):
    # This three class attribute is used for permission logic
    mothers_admin = MotherAdmin(Mother, admin.site)
    mothers_model_name = mothers_admin.opts.model_name
    klass = mothers_admin.opts.model
    # Attribute for database query
    prefetched_list = 'main_document', 'additional_document'
    search_fields = 'name',
    list_per_page = 10
    ordering = '-created',
    # list_display_links = 'custom_name',
    list_display = 'custom_name', 'add_main_docs', 'add_additional_docs'
    inlines = [MainInline, AdditionalInline]
    change_list_template = "admin/documents/document/change_list.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.documents_app_label = self.opts.app_label
        self.documents_model_name = self.opts.model_name
        self.klass = self.opts.model  # This three class attribute is used for permission logi
        self.request = None

    class Media:
        css = {
            'all': ('documents/css/add_butt.css',)
        }
        js = 'documents/js/hide_history_link.js', 'documents/js/hide_p_element.js', 'documents/js/hide_document_tab.js',

    def has_module_permission(self, request) -> bool:
        """
        Determines if a user has module-level permission.

        The user is granted full access to the module if they have the base 'view_document' permission.
        Otherwise, access is only granted if the user was specifically assigned to mother instances at the time
        they were created.
        """
        if not request.user.is_authenticated:
            return False

        user_stage = getattr(request.user, 'stage', None)
        # Construct the custom permission name for the user at a specific stage
        custom_permission_name = f'{user_stage}_{self.mothers_model_name}_{request.user.username}'.lower()
        # Base permission name for viewing documents
        document_view_perm_name = 'documents.view_document'
        view_perm = request.user.has_perm(document_view_perm_name)
        # Get all objects assigned to the user on specific stage
        users_mother_objs = get_objects_for_user(user=request.user, perms=custom_permission_name, klass=self.klass)

        mothers_exist = Mother.objects.all().exists()
        return bool(users_mother_objs) or (view_perm and mothers_exist)

    def get_queryset(self, request):
        """
        Returns the queryset of Mother instances based on user permissions.

        Users with the base 'view_document' permission have access to all instances.
        Users with custom permissions are granted access only to the objects they are specifically assigned.
        """
        self.request = request
        queryset = Mother.objects.prefetch_related(*self.prefetched_list)

        user_stage = getattr(request.user, 'stage', None)
        # Construct the custom permission name for the user at a specific stage
        custom_permission_name = f'{user_stage}_{self.mothers_model_name}_{request.user.username}'.lower()
        # Base permission name for viewing documents
        document_view_perm_name = 'documents.view_document'
        view_perm = request.user.has_perm(document_view_perm_name)

        if view_perm:
            return queryset
        else:
            queryset = get_objects_for_user(user=request.user, perms=custom_permission_name, klass=self.klass)
            return queryset

    def has_view_permission(self, request, mother_instance: Mother = None):
        """
        Determines if a user has view permission.

        If the user has the base 'view_document' permission, they are granted full access to both the list and
        individual object levels. Otherwise, access is only granted if the user was specifically assigned to
        the mother instances when they were created.
        """

        user_stage = getattr(request.user, 'stage', None)
        # Construct the custom permission name for the user at a specific stage
        custom_permission_name = f'{user_stage}_{self.mothers_model_name}_{request.user.username}'.lower()
        custom_perm = request.user.has_perm(custom_permission_name, mother_instance)
        # Base permission name for viewing documents
        document_view_perm_name = 'documents.view_document'
        view_perm = request.user.has_perm(document_view_perm_name)
        # Get all objects assigned to the user on specific stage
        users_mother_objs = get_objects_for_user(user=request.user, perms=custom_permission_name, klass=self.klass)

        if mother_instance:
            return custom_perm or view_perm
        else:
            return bool(users_mother_objs or view_perm)

    def has_change_permission(self, request, mother_instance: Mother = None):
        """
        Determines if a user has change permissions.

        The user is granted full access to both the list and individual object levels if they have
        the base 'change_document' permission.
        If not, access is only granted if the user was specifically assigned to the mother instances when they were
        created and if the 'documents' parameter is present in the request.
        """

        user_stage = getattr(request.user, 'stage', None)
        # Construct the custom permission name for the user at a specific stage
        custom_permission_name = f'{user_stage}_{self.mothers_model_name}_{request.user.username}'.lower()
        custom_perm = request.user.has_perm(custom_permission_name, mother_instance)
        # Base permission name for changing documents
        document_change_perm_name = 'documents.change_document'
        change_perm = request.user.has_perm(document_change_perm_name)
        # Get all objects assigned to the user on specific stage
        users_mother_objs = get_objects_for_user(user=request.user, perms=custom_permission_name, klass=self.klass)

        if 'documents' in request.GET:
            if mother_instance:
                return custom_perm or change_perm
            else:
                return bool(users_mother_objs or change_perm)
        else:
            return False

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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # new button add in case when user change or add new documents
        if request.GET:
            extra_context['custom_buttons_template'] = 'admin/documents/document/custom_buttons.html'
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
                custom_url = reverse('admin:documents_document_change', args=(obj.id,))
                return HttpResponseRedirect(custom_url)
        return response

    @admin.display(description='Name')
    def custom_name(self, obj):
        """
           Renders the 'name' field in the admin list view with conditional clickability.

           This method adds hidden data to indicate whether the 'Mother' instance has related documents.
           If related documents exist, the 'name' field is a clickable link; otherwise, it is plain text.
        """
        hidden_data = format_html('<span class="hidden-data" data-related-docs="{}"></span>', obj.has_related_documents)
        if obj.has_related_documents:
            url = reverse('admin:documents_document_change', args=[obj.pk])
            return format_html('{}<a href="{}">{}</a>', hidden_data, url, obj.name)
        return format_html('{}{}', hidden_data, obj.name)

    @admin.display(description='Main Docs')
    def add_main_docs(self, mother_instance: Mother) -> str:
        main_docs_amount = mother_instance.main_document.count()
        # Construct the URL for the admin change page
        url = reverse('admin:documents_document_change', args=(mother_instance.pk,))

        # Copy filters from the request and add custom parameters
        filters = {key: value for key, value in self.request.GET.items()}
        filters['mother'] = mother_instance.pk
        filters['documents'] = 'main'

        # Construct the query string
        query_string = '&'.join([f'{key}={value}' for key, value in filters.items()])

        # Construct the final URL with query parameters
        full_url = f'{url}?{query_string}'

        # Return the HTML link
        view_perm = self.request.user.has_perm('documents.view_document')
        if view_perm and not self.request.user.is_superuser:
            return format_html('{}', main_docs_amount)
        return format_html('<a href="{}">{} of 10</a>', full_url, main_docs_amount)

    @admin.display(description='Additional Docs')
    def add_additional_docs(self, mother_instance: Mother) -> str:

        additional_docs_amount = mother_instance.additional_document.count()
        # Construct the URL for the admin change page
        url = reverse('admin:documents_document_change', args=(mother_instance.pk,))

        # Copy filters from the request and add custom parameters
        filters = {key: value for key, value in self.request.GET.items()}
        filters['mother'] = mother_instance.pk
        filters['documents'] = 'additional'

        # Construct the query string
        query_string = '&'.join([f'{key}={value}' for key, value in filters.items()])

        # Construct the final URL with query parameters
        full_url = f'{url}?{query_string}'

        # Return the HTML link
        view_perm = self.request.user.has_perm('documents.view_document')
        if view_perm and not self.request.user.is_superuser:
            return format_html('{}', additional_docs_amount)
        return format_html('<a href="{}">{}</a>', full_url, additional_docs_amount)

    def get_inline_instances(self, request, obj=None):
        """Assign custom names for inlines."""
        inline_instances = super().get_inline_instances(request, obj)
        for inline in inline_instances:
            if isinstance(inline, MainInline):
                inline.verbose_name = 'Main Document'
                inline.verbose_name_plural = 'Main Documents'
            elif isinstance(inline, AdditionalDocument):
                inline.verbose_name = 'Additional Document'
                inline.verbose_name_plural = 'Additional Documents'
        return inline_instances

    def get_urls(self):
        """
        Extend the default URL patterns with custom download URLs for main and required documents.
        """
        urls = super().get_urls()
        custom_urls = [
            path('download_main/<int:document_id>/', self.admin_site.admin_view(self.download_file),
                 name='document_main_download'),
            path('download_additional/<int:document_id>/', self.admin_site.admin_view(self.download_additional_file),
                 name='document_additional_download'),
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
    def download_additional_file(request, document_id):
        """
        Handle file download for a given additional document ID.
        """
        try:
            document = AdditionalDocument.objects.get(id=document_id)
            response = FileResponse(document.file.open(), as_attachment=True, filename=document.file.name)
            return response
        except AdditionalDocument.DoesNotExist:
            raise Http404("Document does not exist")
