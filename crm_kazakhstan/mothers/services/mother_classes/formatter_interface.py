from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Union

from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.db import models

from mothers.models import State, Ban, Planned


# Abstract Base Class
class TimeFormatter(ABC):
    def format(self, dt: Optional[datetime]) -> Optional[str]:
        """Template method that defines the algorithm's structure."""
        if not dt:
            return
        return self.format_time(dt)

    @abstractmethod
    def format_time(self, dt: datetime) -> str:
        """Abstract method that subclasses must implement."""
        pass


# Concrete Subclasses
class DayMonthHourMinuteFormatter(TimeFormatter):
    def format_time(self, dt: datetime) -> str:
        """Concrete implementation for 'Day Month Hour:Minute' format."""
        return dt.strftime("%d %B %H:%M")


class BoldDayMonthYearHourMinuteFormatter(TimeFormatter):
    def format_time(self, dt: datetime) -> str:
        """Concrete implementation for bold 'Day Month Year / Hour:Minute' format."""
        formatted_datetime = dt.strftime("%d %B %y/%H:%M")
        return format_html(f'<strong>{formatted_datetime}</strong>')


"""
----------------------------------------------------------------------------------------------------------
"""


# Strategy Pattern: The TextExtractor base class and its subclasses represent the Strategy pattern.
class TextExtractor:
    # Abstract base class for extracting text from objects.
    def extract_text(self, obj: models) -> Optional[str]:
        """Should be implemented by subclasses to extract text from the given object."""
        raise NotImplementedError


class StateExtractor(TextExtractor):
    # Concrete implementation of TextExtractor for State objects.
    def extract_text(self, obj: State) -> Optional[str]:
        """Extracts and returns the state or reason from a State object."""
        state = obj.get_condition_display()
        reason = obj.reason

        if reason or obj.condition:
            return state if obj.condition else reason
        return


class PlanExtractor(TextExtractor):
    # Concrete implementation of TextExtractor for Planned objects.
    def extract_text(self, obj: Planned) -> Optional[str]:
        """Returns the plan from a Planned object."""
        return obj.get_plan_display()


# Decorator Pattern: The CombinedExtractor class acts as a decorator for TextExtractor instances.
class CombinedExtractor(TextExtractor):
    # Combines multiple text extractors.
    def __init__(self, extractor):
        self.extractor = extractor

    def extract_text(self, obj) -> Optional[str]:
        """Uses the provided extractor to extract text from the given object."""
        text = self.extractor.extract_text(obj)
        if text:
            return text
        return


# Template Method Pattern: The TextReducer class uses the Template Method pattern.
class TextReducer:
    # Reduces text from a Ban or State object.
    def __init__(self, textractor: TextExtractor):
        self.textractor = textractor

    def reduce_text(self, instance: Union[Ban, State]) -> format_html:
        """
        Retrieves and reduces the text for a Ban or State object, and formats it in bold HTML.
        """
        text = self.textractor.extract_text(instance)
        if text:
            shortened = (text[:50] + '...') if len(text) > 50 else text
            return mark_safe(f'<strong>{shortened}</strong>')
        return
