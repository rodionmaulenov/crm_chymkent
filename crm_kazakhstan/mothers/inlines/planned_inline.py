from django.contrib import admin

from mothers.models import Planned


class PlannedInline(admin.TabularInline):
    model = Planned
    fields = ('plan', 'note', 'scheduled_date')
    extra = 0

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "plan" and request.user.has_perm('mothers.to_manager_on_primary_stage'):
            kwargs["choices"] = [
                ('', Planned.PlannedChoices.__empty__),
                (Planned.PlannedChoices.TAKE_TESTS.value, Planned.PlannedChoices.TAKE_TESTS.label)
            ]
        else:
            kwargs["choices"] = [('', Planned.PlannedChoices.__empty__)]
        return super().formfield_for_choice_field(db_field, request, **kwargs)