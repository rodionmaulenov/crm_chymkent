from django.contrib import admin
from django.db import transaction, models
from django.utils.translation import ngettext
from django.contrib import messages

from mothers.models import Comment
from revoke_mothers.models import RevokeMother

Comment: models


@admin.register(RevokeMother)
class RevokeMotherAdmin(admin.ModelAdmin):
    ordering = ('-date_create',)
    empty_value_display = "-empty-"
    actions = ('mother_return',)
    list_display = (
        'id', 'name', 'number', 'program', 'residence', 'height_and_weight',
        'bad_habits', 'caesarean', 'children_age', 'age', 'citizenship', 'blood', 'maried',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(comment__banned=True)

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'mother_return' in actions and not request.user.has_perm('mothers.return_mothers'):
            del actions['mother_return']

        return actions

    @transaction.atomic
    @admin.action(description="Return mothers")
    def mother_return(self, request, queryset):
        mother = queryset.count()
        Comment.objects.filter(mother__in=queryset).update(banned=False)
        self.message_user(
            request,
            ngettext(
                f"{mother} mother was successfully restore.",
                f"{mother} mothers were successfully restore.",
                mother
            ),
            messages.SUCCESS,
        )
