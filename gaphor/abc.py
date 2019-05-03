import abc
from zope.interface import implementer


class ActionProvider(metaclass=abc.ABCMeta):
    """
    An action provider is a special service that provides actions
    (see gaphor/action.py) and the accompanying XML for the UI manager.
    """

    menu_xml = "The menu XML"

    action_group = "The accompanying ActionGroup"
