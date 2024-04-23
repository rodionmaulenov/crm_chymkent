from urllib.parse import urlencode

from django.contrib import messages
from django.http import HttpRequest
from django.utils.html import mark_safe
from django.db import models


class URLComponent:
    """Component interface that all concrete components and decorators inherit from."""

    def construct_url(self, text_link=None):
        raise NotImplementedError


class BaseURL(URLComponent):
    """Concrete component that holds the basic structure of the URL."""

    def __init__(self, base_path: str):
        self.base_path = base_path

    def construct_url(self, text_link=None):
        return self.base_path


class URLDecorator(URLComponent):
    """Decorator abstract class that follows the same interface as URLComponent."""

    def __init__(self, url_component: URLComponent):
        self.component = url_component

    def construct_url(self, text_link=None):
        return self.component.construct_url()


class QueryParameterDecorator(URLDecorator):
    """Concrete decorator to add query parameters to the URL."""

    def __init__(self, url_component: URLComponent, params: dict):
        super().__init__(url_component)
        self.params = params

    def construct_url(self, text_link=None):
        base_url = super().construct_url()
        query_string = urlencode(self.params)
        url = f"{base_url}?{query_string}" if query_string else base_url
        if text_link:
            return mark_safe(f'<a href="{url}" ><b>{text_link}</b></a>')
        return url


class MessageDecorator(URLDecorator):
    """Concrete decorator to add messaging after an action."""

    def __init__(self, url_component: URLComponent, request: HttpRequest, message: str, level: int = messages.INFO):
        super().__init__(url_component)
        self.request = request
        self.message = message
        self.level = level

    def construct_url(self, text_link=None):
        self._add_message()
        return super().construct_url()

    def _add_message(self):
        """Add a message to the Django messages framework."""
        messages.add_message(self.request, self.level, self.message)
