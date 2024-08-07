from django.core.exceptions import ValidationError


def validate_max_length(value):
    if len(value) > 300:
        raise ValidationError(
            'This field cannot exceed 300 characters.'
        )
