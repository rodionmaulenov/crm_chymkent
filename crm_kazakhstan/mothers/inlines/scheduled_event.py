from django.contrib import admin
from mothers.models.mother import ScheduledEvent
from django import forms

from mothers.services.application import convert_utc_to_local


class ScheduledEventForm(forms.ModelForm):
    class Meta:
        model = ScheduledEvent
        fields = '__all__'
        widgets = {
            'note': forms.Textarea(attrs={'rows': 5, 'cols': 45, 'maxlength': 300}),
        }


class ScheduledEventInline(admin.TabularInline):
    model = ScheduledEvent
    form = ScheduledEventForm
    extra = 1
    fields = 'mother', 'note', 'scheduled_time', 'is_completed', 'custom_scheduled_time'
    readonly_fields = ('custom_scheduled_time',)
    max_num = 1

    class Media:
        css = {
            'all': ('questionnaire/css/text_move_another_line_note.css',)
        }

        js = 'questionnaire/js/text_move_another_line_note.js',

    def get_fields(self, request, obj=None):
        # cases when add/change
        if request.GET.get('add_or_change') == 'add':
            return 'mother', 'note', 'scheduled_time'
        elif request.GET.get('add_or_change') == 'change':
            return 'mother', 'note', 'scheduled_time', 'is_completed'
        else:
            # cases when read
            return 'note', 'custom_scheduled_time', 'is_completed'

    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)
        # When change or add inline instance
        if request.GET.get('add_or_change', False):
            # Return only incomplete events
            return qs.filter(is_completed=False)
        # When view inline instances
        return qs

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        if obj:
            # Allow adding only if no incomplete events exist
            if ScheduledEvent.objects.filter(mother=obj, is_completed=False).exists():
                return False
        return True

    def has_change_permission(self, request, obj=None):
        # When view inline instances
        if not request.GET.get('add_or_change'):
            return False
        return True

    def custom_scheduled_time(self, obj):
        local_datetime = convert_utc_to_local(self.request, obj.scheduled_time)
        return local_datetime.strftime("%B %d, %Y, %H:%M")

    custom_scheduled_time.short_description = 'Scheduled Time'
