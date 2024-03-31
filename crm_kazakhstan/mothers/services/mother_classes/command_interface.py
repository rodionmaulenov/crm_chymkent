# This code demonstrates the use of the Command Design Pattern and the Chain of Responsibility
# Design Pattern in Python to handle different conditions related to a `Mother` object in a system.
# The Command Pattern is used to encapsulate actions as objects, and the Chain of Responsibility
# Pattern is used to determine which command to execute based on the provided conditions.


from abc import ABC, abstractmethod
from typing import Optional, Union

from mothers.models import Mother, Planned, Ban, State
from mothers.services.mother import add_new, change


class ConditionCommand(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs) -> Optional[str]:
        """Abstract method to be implemented by concrete commands."""
        pass


# Concrete Commands
class EmptyCommand(ConditionCommand):
    def execute(self, *args, **kwargs) -> None:
        """Concrete command that does nothing."""
        return


class AddNewCommand(ConditionCommand):
    def execute(self, *args, **kwargs) -> str:
        """Concrete command to add a new Mother object."""
        path: str = kwargs.get('add_url')
        mother: Mother = kwargs.get('mother')
        return add_new(path, mother)


class ChangeCommand(ConditionCommand):
    def execute(self, *args, **kwargs) -> str:
        """Concrete command to change a Mother object."""
        path: str = kwargs.get('change_url')
        obj: Union[Planned, Ban, State] = kwargs.get('obj')
        text: str = kwargs.get('text')
        return change(path, obj, text)


# Handler Interface
class CommandHandler(ABC):
    def __init__(self) -> None:
        self._next_handler: Optional[CommandHandler] = None

    def set_next(self, handler: 'CommandHandler') -> 'CommandHandler':
        """Sets the next handler in the chain."""
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, state: bool, plan: bool, ban: bool) -> ConditionCommand:
        """Abstract method to handle the request or pass it to the next handler."""
        if self._next_handler:
            return self._next_handler.handle(state, plan, ban)


# Concrete Handlers for "State"
class PlanOrBanHandler(CommandHandler):
    def handle(self, state: bool, plan: bool, ban: bool) -> ConditionCommand:
        """Handler for the case when plan or ban is true."""
        if not state and (plan or ban):
            return EmptyCommand()
        return super().handle(state, plan, ban)


class BanOrStateHandler(CommandHandler):
    def handle(self, state: bool, plan: bool, ban: bool) -> ConditionCommand:
        """Handler for the case when state or ban is true."""
        if not plan and (ban or state):
            return EmptyCommand()
        return super().handle(state, plan, ban)


class NoOneHandler(CommandHandler):
    def handle(self, state: bool, plan: bool, ban: bool) -> ConditionCommand:
        """Handler for the case when all flags are false."""
        if not state and not plan and not ban:
            return AddNewCommand()
        return super().handle(state, plan, ban)


class StateHandler(CommandHandler):
    def handle(self, state: bool, plan: bool, ban: bool) -> ConditionCommand:
        """Handler for the case when only the state flag is true."""
        if state and not plan and not ban:
            return ChangeCommand()
        return super().handle(state, plan, ban)


class PlanHandler(CommandHandler):
    def handle(self, state: bool, plan: bool, ban: bool) -> ConditionCommand:
        """Handler for the case when only the plan flag is true."""
        if plan and not ban and not state:
            return ChangeCommand()
        return super().handle(state, plan, ban)


# Client Code For Creating ``State`` Instance
def get_command(state: bool, plan: bool, ban: bool):
    """
    Create a chain for "State" conditions. Depending on the conditions,
    it returns an appropriate command for adding, changing, or performing another action.
    """
    handler1 = PlanOrBanHandler()
    handler2 = NoOneHandler()
    handler3 = StateHandler()

    handler1.set_next(handler2).set_next(handler3)

    return handler1.handle(state, plan, ban)


def get_command2(state: bool, plan: bool, ban: bool):
    """
    Create a chain for "Planned" conditions. Depending on the conditions,
    it returns an appropriate command for adding, changing, or performing another action.
    """
    handler1 = BanOrStateHandler()
    handler2 = NoOneHandler()
    handler3 = PlanHandler()

    handler1.set_next(handler2).set_next(handler3)

    return handler1.handle(state, plan, ban)
