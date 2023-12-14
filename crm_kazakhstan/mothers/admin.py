from datetime import datetime

import pytz
from dateutil import parser

from django.contrib import admin
from django.db import models
from django.utils.translation import ngettext
from django.contrib import messages
from django.utils import formats, timezone

from mothers.filters import AuthConditionListFilter
from mothers.inlines import ConditionInline, CommentInline
from mothers.models import Mother, Comment
# from mothers.services import get_difference_time

Mother: models
Comment: models


@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    ordering = ('-date_create',)
    inlines = [ConditionInline, CommentInline]
    list_filter = ("date_create", AuthConditionListFilter)
    list_display = (
        'id', 'name', 'your_date_created', 'number', 'residence', 'height_and_weight',
        'bad_habits', 'caesarean', 'children_age', 'age', 'citizenship', 'blood', 'maried',
    )

    actions = ('delete_selected', 'make_revoke')

    list_display_links = ('name', 'residence',)
    readonly_fields = ('your_date_created',)
    search_fields = ('number', 'program', 'residence__icontains',)
    view_on_site = False
    fieldsets = [
        (
            None,
            {
                "fields": [(
                    'name', 'number', 'program', 'residence', 'height_and_weight', 'your_date_created',
                    'bad_habits', 'caesarean', 'children_age', 'age', 'citizenship', 'blood', 'maried'
                ), ],

                'description': 'This is the additional information section.',
            },
        ),
        (
            "Advanced options",
            {
                "classes": ['collapse'],
                "fields": [],
            },
        ),
    ]

    search_help_text = 'IN DATA QUERY USE PATTERNS LIKE  "D-M-Y"  "D-M"  "D"'

    def __init__(self, *args, **kwargs):
        self.request = None
        super().__init__(*args, **kwargs)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            local_datetime = datetime.combine(instance.scheduled_date, instance.scheduled_time)
            utc_datetime = local_datetime.astimezone(pytz.utc)
            instance.scheduled_date = utc_datetime.date()
            instance.scheduled_time = utc_datetime.time()
            instance.save()
        formset.save_m2m()
        return super().save_formset(request, form, formset, change)

    def get_formsets_with_inlines(self, request, obj=None):
        """
        Perform before save_formset method
        """
        for inline in self.get_inline_instances(request, obj):
            yield inline.get_formset(request, obj), inline

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'make_revoke' in actions and not request.user.has_perm('mothers.revoke_mothers'):
            del actions['make_revoke']
        return actions

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            if search_term[:4].isdigit():
                search_date = parser.parse(search_term).date()
            else:
                search_date = parser.parse(search_term, dayfirst=True).date()

            queryset |= self.model.objects.filter(date_create__gt=search_date)
        except parser.ParserError:
            pass

        return queryset, use_distinct

    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)
        qs = qs.exclude(comment__revoked=True)
        return qs

    @admin.action(description="Revoke mothers")
    def make_revoke(self, request, queryset):
        mother = queryset.count()
        Comment.objects.filter(mother__in=queryset).update(revoked=True)

        for mother in queryset.exclude(comment__isnull=False):
            Comment.objects.create(mother=mother, revoked=True)

        self.message_user(
            request,
            ngettext(
                f"{mother} mother was successfully revoked.",
                f"{mother} mothers were successfully revoked.",
                mother
            ),
            messages.SUCCESS,
        )

    @admin.display(empty_value="no date", description='date created')
    def your_date_created(self, obj):
        user_timezone = getattr(self.request, 'timezone', 'UTC')

        user_tz = pytz.timezone(user_timezone)
        local_time = timezone.localtime(obj.date_create, timezone=user_tz)
        formatted_date = formats.date_format(local_time, "j M H:i")
        return formatted_date

    admin.site.disable_action('delete_selected')

    # @admin.display(empty_value="unknown", description='Documents')
    # def formatted_document_list(self, mother: Mother) -> str:
    #     """
    #     From instance verifies if all related documents exist return check mark
    #     otherwise return list documents that are not exist
    #
    #     :param mother: Mother model.Models
    #     :return: html string
    #     """
    #     actual_document_names = {
    #         'метрика ребенка', 'метрика мамы', 'нет судимости', 'нарколог', 'психиатр',
    #         'не в браке', 'загранпаспорт'
    #     }
    #     document_names = Mother.objects.filter(pk=mother.pk).values_list('document__name', flat=True)
    #
    #     if len(document_names) == 7:
    #         custom_icon_html = '<img src="/static/admin/img/icon-yes.svg" alt="True" style="width: 20px; height: 20px;" />'
    #         return format_html(custom_icon_html)
    #     else:
    #         html_string = '<div><select>'
    #
    #         for document_name in actual_document_names:
    #             if not (document_name in document_names):
    #                 html_string += f'<option>{document_name}</option>'
    #
    #         html_string += '</select></div>'
    #
    #         return format_html(html_string)
