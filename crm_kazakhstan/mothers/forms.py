from typing import Dict, Any

from django import forms
from django.db import models

from mothers.models import State, Planned

from ban.models import Ban

Mother: models


class StateAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        from mothers.services.state import initialize_form_fields, set_initial_mother_value_on_add, \
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
        """
        Cleans the data of the form and applies validations.
        """
        from mothers.services.state import if_field_error_exists

        cleaned_data = super().clean()
        # check each field, that not have error
        if_field_error_exists(self, cleaned_data)

        return cleaned_data

    class Meta:
        model = State
        fields = '__all__'


class PlannedAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        from mothers.services.state import initialize_form_fields, set_initial_mother_value_on_add, \
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

    class Meta:
        model = Planned
        fields = '__all__'


class BanAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        from mothers.services.state import set_initial_mother_value_on_add, hide_mother_field_on_add
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Hide the mother field
        hide_mother_field_on_add(self)
        # Set the mother's ID as the initial value
        set_initial_mother_value_on_add(self, request)

    class Meta:
        model = Ban
        fields = '__all__'


class DocumentAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        from mothers.services.state import set_initial_mother_value_on_add, hide_mother_field_on_add
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Hide the mother field
        hide_mother_field_on_add(self)
        # Set the mother's ID as the initial value
        set_initial_mother_value_on_add(self, request)

    class Meta:
        model = Ban
        fields = '__all__'

