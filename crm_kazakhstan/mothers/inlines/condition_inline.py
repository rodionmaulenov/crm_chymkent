from django.contrib import admin
from django.forms import BaseInlineFormSet
from django import forms
from django.utils.html import format_html

from mothers.constants import CONDITION_CHOICES
from mothers.services.mother import convert_utc_to_local, by_date_or_by_datatime
from mothers.models import Condition


class EmptyOnlyFieldWrapper:
    """
    This class exists only for pre-populate form that will render "empty" string if field blank,
    or the actual value in a span for specific fields when instance.finished is True.
    """

    def __init__(self, widget, field_name=None, finished=False):
        self.original_widget = widget
        self.field_name = field_name
        self.finished = finished

    def render(self, name, value, attrs=None, renderer=None):

        if self.finished and self.field_name in ['scheduled_date', 'scheduled_time']:
            return format_html('<span>{}</span>', value or 'empty')

        elif self.finished and self.field_name == 'condition':
            long_description = dict(CONDITION_CHOICES).get(value)
            return format_html('<span>{}</span>', long_description)

        elif value:
            return self.original_widget.render(name, value, attrs, renderer)

        else:
            return format_html('<span>{}</span>', 'empty')

    @property
    def needs_multipart_form(self):
        return self.original_widget.needs_multipart_form

    @property
    def is_hidden(self):
        return self.original_widget.is_hidden

    @property
    def use_required_attribute(self):
        return self.original_widget.use_required_attribute

    @property
    def attrs(self):
        return self.original_widget.attrs

    @property
    def value_omitted_from_data(self):
        return self.original_widget.value_omitted_from_data

    @property
    def value_from_datadict(self):
        return self.original_widget.value_from_datadict

    @property
    def supports_microseconds(self):
        # Delegate the supports_microseconds to the original widget
        return getattr(self.original_widget, 'supports_microseconds', False)


class ConditionInlineFormWithoutFinished(forms.ModelForm):
    class Meta:
        model = Condition
        fields = ('condition', 'reason', 'scheduled_date', 'scheduled_time')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        finished = self.instance.finished if self.instance else False

        # If finished = True instance stand be not changeable
        if finished:
            for field in self.fields:
                self.fields[field].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        scheduled_time = cleaned_data.get("scheduled_time")
        scheduled_date = cleaned_data.get("scheduled_date")

        if scheduled_time and not scheduled_date:
            self.add_error('scheduled_date', "Date must be provided if time is set.")

        return cleaned_data


class ConditionInlineFormWithFinished(ConditionInlineFormWithoutFinished):
    class Meta:
        model = Condition
        fields = '__all__'


class CustomConditionInlineFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            if form.instance.pk:
                utc_date = form.instance.scheduled_date
                utc_time = form.instance.scheduled_time
                if utc_date and utc_time:
                    # Convert UTC date and time to user's local timezone
                    local_datetime = convert_utc_to_local(self.request, utc_date, utc_time)
                    # Update the initial time of the form
                    form.initial['scheduled_time'] = local_datetime.time()
                    form.initial['scheduled_date'] = local_datetime.date()

    def _construct_form(self, i, **kwargs):
        """
        Customizes field rendering for special fields when the instance is finished.
        """
        form = super()._construct_form(i, **kwargs)
        finished = form.instance.finished if form.instance else False

        for field_name, field_inst in form.fields.items():
            if field_name not in ['finished', 'DELETE']:
                is_special_field = field_name in ['scheduled_date', 'scheduled_time', 'condition']
                form.fields[field_name].widget = EmptyOnlyFieldWrapper(
                    field_inst.widget,
                    field_name=field_name,
                    finished=finished and is_special_field
                )

        return form


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 0
    formset = CustomConditionInlineFormset
    form = ConditionInlineFormWithoutFinished
    max_num = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super().get_formset(request, obj, **kwargs)

        # increase max_num by 1 if mother instance from changelist url
        res = obj.condition_set.filter(finished=True).count()
        time = by_date_or_by_datatime(request)
        if res >= 0 and not time:
            formset_class.max_num = res + 1

        formset_class.request = request
        return formset_class
