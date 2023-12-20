from django.contrib import admin
from mothers.models import PrimaryVisit


@admin.register(PrimaryVisit)
class PrimaryVisitAdmin(admin.ModelAdmin):
    list_display = ('name',)
