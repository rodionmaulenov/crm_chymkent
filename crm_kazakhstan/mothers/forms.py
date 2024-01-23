from typing import Dict, Any

from django import forms
from django.db import models

from mothers.models import Condition

Mother: models


class ConditionAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        from mothers.services.condition import initialize_form_fields, set_initial_mother_value_on_add, \
            hide_mother_field_on_add
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Hide the mother field
        hide_mother_field_on_add(self)
        # Set the mother's ID as the initial value
        set_initial_mother_value_on_add(self, request)

        # Paste user local timezone date and time into form fields
        # Before form render on change_page
        initialize_form_fields(self, request)

    def clean(self) -> Dict[str, Any]:
        from mothers.services.condition import validate_condition_with_date, validate_time_date_dependencies, \
            validate_condition_without_date
        """Cleans the data of the form and applies validations."""
        cleaned_data = super().clean()
        validate_time_date_dependencies(self, cleaned_data)
        validate_condition_with_date(self, cleaned_data)
        validate_condition_without_date(self, cleaned_data)
        return cleaned_data

    class Meta:
        model = Condition
        fields = '__all__'


class AddConditionAdminForm(ConditionAdminForm):
    class Meta:
        model = Condition
        fields = ['mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time']


class ChangeConditionAdminForm(ConditionAdminForm):
    class Meta:
        model = Condition
        fields = ['mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time', 'finished']
