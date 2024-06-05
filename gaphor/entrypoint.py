import functools
import importlib.metadata
import inspect
import logging
from typing import Dict, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


def initialize(scope, services=None, **known_services: T) -> Dict[str, T]:
    return init_entry_points(load_entry_points(scope, services), **known_services)


@functools.lru_cache(maxsize=4)
def list_entry_points(group):
    return importlib.metadata.entry_points(group=group)


def load_entry_points(scope, services=None) -> Dict[str, type]:
    """Load services from resources."""
    uninitialized_services = {}
    for ep in list_entry_points(scope):
        if not services or ep.name in services:
            cls = ep.load()
            logger.debug(f'found entry point "{scope}.{ep.name}"')
            uninitialized_services[ep.name] = cls
    return uninitialized_services


def init_entry_points(
    uninitialized_services: Dict[str, type[T]], **known_services: T
) -> Dict[str, T]:
    """Instantiate service definitions, taking into account dependencies
    defined in the constructor.

    Given a dictionary `{name: service-class}`, return a map `{name:
    service-instance}`.
    """
    ready: Dict[str, T] = known_services.copy()

    def pop(name):
        try:
            return uninitialized_services.pop(name)
        except KeyError:
            return None

    def init(name, cls):
        kwargs = {}
        for param_name, param in inspect.signature(cls).parameters.items():
            if param_name not in ready:
                depcls = pop(param_name)
                if depcls:
                    kwargs[param_name] = init(param_name, depcls)
                elif param.default is inspect.Parameter.empty:
                    logger.warn(
                        "Entrypoint %s parameter %s does not reference a resolved dependency",
                        name,
                        param_name,
                    )
            else:
                kwargs[param_name] = ready[param_name]
        srv = cls(**kwargs)
        ready[name] = srv
        return srv

    while uninitialized_services:
        name = next(iter(uninitialized_services.keys()))
        cls = pop(name)
        init(name, cls)

    return ready
