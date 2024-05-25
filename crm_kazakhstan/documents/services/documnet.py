from documents.models import MainDocument, RequiredDocument
from documents.services.builders import HtmlBuilder

from mothers.models import Mother
from mothers.services.mother_classes.command_interface import Command
from mothers.services.mother_classes.url_decorators import BaseURL, QueryParameterDecorator

from django.urls import reverse
from django.http import HttpRequest
from django.utils.html import format_html
from django.templatetags.static import static


class IEndPoint:
    @property
    def change_url(self):
        return BaseURL(reverse('admin:documents_documentproxy_change', args=(self.obj.pk,)))

    def queries(self):
        filters = {key: value for key, value in self.request.GET.items()}
        filters['mother'] = self.obj.pk
        return filters

    def construct_uri(self):
        base_url = self.change_url
        add_url_with_query = QueryParameterDecorator(base_url, self.queries())
        endpoint = add_url_with_query.construct_url()
        return endpoint


class MainEndPoint(IEndPoint):
    def queries(self):
        queries = super().queries()
        # add to query new keyword for url
        queries['documents'] = 'main'
        return queries


class ProgressBarADD(Command, IEndPoint):
    len_documents = 0
    # Set the fixed width of the outer div
    container_width = 60

    def __init__(self, request: HttpRequest, obj: Mother):
        self.request = request
        self.obj = obj
        self.percentage = self.get_percentage()
        self.color = self.choose_color()
        self.user = self.request.user

    def documents(self):
        raise NotImplementedError("You should implement this method.")

    def get_percentage(self):
        max_count = self.len_documents  # Or dynamically calculate the max count if needed
        document_count = self.documents()  # Adjust to your related documents field name
        percentage = (document_count / max_count) * 100
        return percentage

    def choose_color(self):
        # Choose color based on percentage
        if self.percentage < 30:
            color = '#dc3545'  # Red for less than 30%
        elif self.percentage < 99:
            color = '#ffc107'  # Yellow for 30-99%
        else:
            color = '#28a745'  # Green for 99% and above
        return color

    def set_button(self, builder):
        """Choose button consider the amount of documents."""
        user_has_permission = self.user.has_perm('documents.view_documentproxy')
        superuser = self.user.is_superuser

        if self.documents() > 0:
            change = static('documents/img/pencil.png')
            change_icon = f'<img src="{change}" class="change-icon">'
            builder.add_child_fluent(
                name='a',
                href='{}',
                cls=f'add-change-link {"disabled-link" if user_has_permission and not superuser else ""}',
                text=change_icon + ' Change'
            )

        if self.documents() == 0:
            plus = static('documents/img/plus.jpeg')
            plus_icon = f'<img src="{plus}" class="add-icon">'
            builder.add_child_fluent(
                name='a',
                href='{}',
                cls=f'add-change-link {"disabled-link" if user_has_permission and not superuser else ""}',
                text=plus_icon + ' Add'
            )
        return builder

    @staticmethod
    def progress_bar(builder):
        """Generate progress bar"""
        builder.add_child_fluent(
            name='div',
            style='display: flex; align-items: center;'
        ).add_child_fluent(
            name='div',
            style='width: {}px; background-color: #eee; border: 1px solid #ccc; '
                  'border-radius: 10px; position: relative; overflow: hidden;'
        ).add_child_fluent(
            name='div',
            style='width: {}%; background-color: {}; height: 9px; border-radius: 10px;'
        ).go_back().go_back()

        return builder

    def execute(self):
        # Generate the HTML for the progress bar and the styled add link
        builder = HtmlBuilder(root_name='div')
        builder_progress_bar = self.progress_bar(builder)
        final_builder = self.set_button(builder_progress_bar)

        endpoint_uri = self.construct_uri()
        progress_bar_html = format_html(str(final_builder), self.container_width, self.percentage, self.color,
                                        endpoint_uri)
        return progress_bar_html


class ProgressBarADDMain(ProgressBarADD):
    len_documents = len(MainDocument.MainDocumentChoice.choices)

    def documents(self):
        return self.obj.maindocument_set.count()

    def queries(self):
        queries = super().queries()
        # add to query new keyword for url
        queries['documents'] = 'main'
        return queries


class ProgressBarADDRequired(ProgressBarADD):
    len_documents = len(RequiredDocument.RequiredDocumentChoice.choices)

    def documents(self):
        return self.obj.requireddocument_set.count()

    def queries(self):
        queries = super().queries()
        # add to query new keyword for url
        queries['documents'] = 'required'
        return queries
