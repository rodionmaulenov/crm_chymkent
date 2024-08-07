from django.contrib import admin
from mothers.models.mother import Laboratory
from django import forms


class LaboratoryInline(admin.TabularInline):
    model = Laboratory
    extra = 1
    fields = 'mother', 'analysis', 'description', 'scheduled_time', 'is_completed'
    max_num = 1

    def has_view_permission(self, request, obj=None):
        return True
