from inspect import getmembers, isclass, isabstract

from . import manager


class ManagerFactory:
    manager_implementations = {}

    def __init__(self):
        self.load_manager_methods()

    def load_manager_methods(self):
        implementation = getmembers(manager, lambda m: isclass(m) and not isabstract(m))
        for name, _type in implementation:
            if isclass(_type) and issubclass(_type, manager.Manager):
                self.manager_implementations[name] = _type

    def create(self, manager_type: str):
        if manager_type in self.manager_implementations:
            return self.manager_implementations[manager_type]()