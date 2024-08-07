from documents.models import MainDocument, AdditionalDocument
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from django import forms
from documents.widget import CustomFileInput
from mothers.services.application import convert_utc_to_local


class AdditionalDocumentForm(forms.ModelForm):
    class Meta:
        model = AdditionalDocument
        fields = '__all__'
        widgets = {
            'file': CustomFileInput,
            'note': forms.Textarea(attrs={'rows': 3, 'cols': 45, 'maxlength': 300}),
        }


class AdditionalInline(admin.TabularInline):
    model = AdditionalDocument
    form = AdditionalDocumentForm
    extra = 1
    fields = ('mother', 'title', 'get_html_photo', 'file', 'note', 'date_create', 'download_link', 'short_file_path')
    readonly_fields = ('date_create', 'download_link', 'get_html_photo', 'short_file_path')
    max_num = len(MainDocument.MainDocumentChoice.choices)

    class Media:
        css = {
            'all': ('documents/css/increase_image_scale.css', 'documents/css/text_move_another_line_note.css')
        }
        js = ('documents/js/redirect_on_additional_docs.js', 'documents/js/hide_document_tab.js',
              'documents/js/text_move_another_line_note.js', "documents/js/increase_image_scale.js",)

    def get_queryset(self, request):
        self.request = request
        return super().get_queryset(request)

    def get_fields(self, request, obj=None):
        # cases when add/change
        if 'documents' in request.GET:
            return 'mother', 'title', 'file', 'note'
        else:
            # cases when read
            return 'short_file_path', 'get_html_photo', 'date_create', 'download_link', 'note'

    def has_view_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        # when redirect on documentproxy directly the inline instances are not changeable.
        if not request.GET:
            return False
        if request.user.is_superuser:
            return True
        # user that only view can only view.
        if request.user.has_perm('documents.view_documentproxy'):
            return False
        return True

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj=None)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj=None)

    def download_link(self, obj):
        if obj.file:
            url = reverse('admin:document_additional_download', args=[obj.id])
            return format_html(
                '<a href="{}"><img src="/static/documents/img/Download.png" alt="Download" width="35" height="35" /></a>',
                url
            )
        return "-"

    download_link.short_description = 'Download'

    def get_html_photo(self, obj):
        if obj.file:
            file_url = obj.file.url
            if file_url.endswith('.pdf'):
                return '-'
            else:
                return mark_safe(f"""
                    <div class='image-container'>
                        <img src='{file_url}' class='hoverable-image' />
                    </div>
                """)

    get_html_photo.short_description = 'Screenshot'

    def date_create(self, obj):

        local_datetime = convert_utc_to_local(self.request, obj.created)
        return local_datetime.strftime("%B %Y, %H:%M")

    date_create.short_description = 'Created'

    def short_file_path(self, obj):
        file_url = obj.file.url
        name_file = obj.file.name.split('/')[1]
        return mark_safe(f" <a href='{file_url}'>{name_file}</a>")

    short_file_path.short_description = 'File'
