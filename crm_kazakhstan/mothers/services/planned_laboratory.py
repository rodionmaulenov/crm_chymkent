from django.db.models import Q, QuerySet


def mothers_which_on_laboratory_stage(Mothers_queryset: QuerySet) -> QuerySet:
    """
    Retrieves Mother instances which planned laboratory visit or wait doctor answer.
    """

    queryset = Mothers_queryset.filter(
        Q(laboratories__is_completed=False) |
        Q(laboratories__doctoranswer__is_completed=False)
    )

    return queryset
