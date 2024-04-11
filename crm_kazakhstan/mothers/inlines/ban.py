from django.contrib import admin
from django.utils.html import format_html

from mothers.models import Ban
from mothers.services.mother import convert_to_local_time
from mothers.services.mother_classes.formatter_interface import DayMonthYearFormatter
from mothers.services.state import render_icon


class BanInline(admin.TabularInline):
    model = Ban
    fields = ("display_comment", 'when_created', 'display_icon')
    readonly_fields = ('display_comment', 'when_created', 'display_icon')
    extra = 0

    class Media:
        css = {
            'all': ('mothers/css/hide-inline-descriptions.css',)
        }

    def get_queryset(self, request):
        self.request = request
        return super().get_queryset(request)

    def has_view_permission(self, request, obj=None):
        return True

    @admin.display(description='comment')
    def display_comment(self, ban: Ban) -> str:
        return format_html('<strong>{}</strong>', ban.comment.upper())

    @admin.display(description='date created')
    def when_created(self, ban: Ban) -> str:
        user_timezone = getattr(self.request.user, 'timezone', 'UTC')
        local_time = convert_to_local_time(ban, user_timezone)
        formatter = DayMonthYearFormatter()
        formatting = formatter.format(local_time)
        return formatting

    @admin.display(description='banned')
    def display_icon(self, obj: Ban) -> str:
        tru_or_false = obj.banned
        return render_icon(tru_or_false)
