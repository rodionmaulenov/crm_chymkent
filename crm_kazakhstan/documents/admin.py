from django.contrib import admin

from documents.models import Document


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'mother', 'document')
    fields = ('mother', 'name', 'document')


admin.site.register(Document, DocumentAdmin)


class DocumentInline(admin.StackedInline):
    model = Document
    extra = 0  # Number of empty forms to display
    raw_id_fields = ('mother',)
