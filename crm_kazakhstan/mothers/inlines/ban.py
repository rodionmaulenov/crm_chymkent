from django.contrib import admin

from mothers.models import Ban
from mothers.services.mother import convert_to_local_time, output_time_format
from mothers.services.state import render_icon


class BanInline(admin.TabularInline):
    model = Ban
    fields = ("display_comment", 'when_created', 'display_banned')
    readonly_fields = ('display_comment', 'when_created', 'display_banned')
    extra = 0

    def get_queryset(self, request):
        self.request = request
        return super().get_queryset(request)

    def has_view_permission(self, request, obj=None):
        return True

    @admin.display(description='comment')
    def display_comment(self, obj: Ban) -> str:
        return obj.comment

    @admin.display(description='created')
    def when_created(self, obj: Ban) -> str:
        user_timezone = getattr(self.request.user, 'timezone', 'UTC')

        local_time = convert_to_local_time(obj, user_timezone)
        return output_time_format(local_time)

    @admin.display(description='banned')
    def display_banned(self, obj: Ban) -> str:
        tru_or_false = obj.banned
        return render_icon(tru_or_false)
