from documents.models import MainDocument
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.urls import reverse

from mothers.services.mother import convert_utc_to_local


class DocumentInline(admin.TabularInline):
    model = MainDocument
    extra = 1
    fields = ('mother', 'title', 'get_html_photo', 'file', 'note', 'date_create', 'download_link')
    readonly_fields = ('date_create', 'download_link', 'get_html_photo')
    max_num = len(MainDocument.MainDocumentChoice.choices)

    class Media:
        js = ('documents/js/remove_duplicates_main.js', 'documents/js/redirect_on_main_docs.js',)

    def get_queryset(self, request):
        self.request = request
        return super().get_queryset(request)

    def get_fields(self, request, obj=None):
        # cases when add/change
        if 'documents' in request.GET:
            return 'mother', 'title', 'file', 'note'
        else:
            # cases when read
            return 'get_html_photo', 'file', 'note', 'date_create', 'download_link'

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
            url = reverse('admin:document_main_download', args=[obj.id])
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

    get_html_photo.short_description = 'Image'

    def date_create(self, obj):
        utc_date = obj.created.date()
        utc_time = obj.created.time()

        local_datetime = convert_utc_to_local(self.request, utc_date, utc_time)
        return local_datetime.strftime("%B %Y, %H:%M")

    date_create.short_description = 'Created'
