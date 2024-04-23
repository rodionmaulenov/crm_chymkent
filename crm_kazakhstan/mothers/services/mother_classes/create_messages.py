from abc import ABC, abstractmethod

from django.db import models
from django.utils.html import mark_safe

from mothers.models import Mother


class IMessageCreator(ABC):
    def __init__(self, obj: models = None, path: str = None):
        self.obj = obj
        self.path = path

    def message(self, custom_text=None) -> str:
        text = self._process_text(custom_text)
        return text

    @abstractmethod
    def _process_text(self, custom_text=None) -> str:
        pass


class MessageCreator(IMessageCreator):

    def _process_text(self, custom_text=None) -> str:
        text = f'{custom_text} {self.get_link()}'
        return mark_safe(text)

    def get_link(self):
        mother = self.obj if isinstance(self.obj, Mother) else self.obj.mother
        return f'<a href="{self.path}" ><b>{mother}</b></a>'
