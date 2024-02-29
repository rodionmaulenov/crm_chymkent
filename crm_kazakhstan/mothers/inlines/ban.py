from django.contrib import admin

from mothers.models import Ban


class BanInline(admin.TabularInline):
    model = Ban
    fields = ("comment", 'created', 'banned')
    readonly_fields = ('created', )
    extra = 0
