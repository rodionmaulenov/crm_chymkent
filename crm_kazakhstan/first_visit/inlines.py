from mothers.inlines import PlannedInline
from mothers.models import Planned


class PrimaryVisitPlannedInline(PlannedInline):
    model = Planned
    fields = ('plan', 'note', 'scheduled_date')
    extra = 0