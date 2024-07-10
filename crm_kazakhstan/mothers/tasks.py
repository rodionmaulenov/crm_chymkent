from celery import shared_task
from django.utils import timezone
from .models import Mother
from django.db.models import Q


@shared_task
def delete_weekday_objects():
    # Exclude instances where any of the specified fields are null
    has_null_fields = Mother.objects.filter(
        Q(age__isnull=True) | Q(residence__isnull=True) | Q(height__isnull=True) | Q(weight__isnull=True) |
        Q(caesarean__isnull=True) | Q(children__isnull=True)
    )

    # Get the current date and time
    date_now = timezone.now()

    mothers_to_delete_ids = []
    for mother in has_null_fields:
        if mother.created.weekday() in [0, 1, 2, 3, 4] and mother.created.date() < date_now.date():
            mothers_to_delete_ids.append(mother.id)

    # Delete the mothers
    deleted, _ = Mother.objects.filter(id__in=mothers_to_delete_ids).delete()

    return deleted


@shared_task
def delete_weekend_objects():
    # Exclude instances where any of the specified fields are null
    has_null_fields = Mother.objects.filter(
        Q(age__isnull=True) | Q(residence__isnull=True) | Q(height__isnull=True) | Q(weight__isnull=True) |
        Q(caesarean__isnull=True) | Q(children__isnull=True)
    )

    # Get the current date and time
    date_now = timezone.now()

    mothers_to_delete_ids = []
    for mother in has_null_fields:
        if mother.created.weekday() in [5, 6] and mother.created.date() < date_now.date():
            mothers_to_delete_ids.append(mother.id)

    # Delete the mothers
    deleted, _ = Mother.objects.filter(id__in=mothers_to_delete_ids).delete()

    return deleted
