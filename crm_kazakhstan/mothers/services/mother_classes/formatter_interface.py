from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from django.utils.html import format_html


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


class DayMonthYearFormatter(TimeFormatter):
    def format_time(self, dt: datetime) -> str:
        """Concrete implementation for 'Day.Month.Year' format."""
        return dt.strftime("%d.%m.%Y")


class HourMinuteFormatter(TimeFormatter):
    def format_time(self, dt: datetime) -> str:
        """Concrete implementation for 'Hour:Minute' format."""
        return dt.strftime("%H:%M")
