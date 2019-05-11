from .extension import ExtensionItem
from .metaclass import MetaclassItem


def _load():
    from . import extensionconnect, metaclasseditor, stereotypepage


_load()
