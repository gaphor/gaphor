from gaphor.diagram.profiles.extension import ExtensionItem
from gaphor.diagram.profiles.metaclass import MetaclassItem


def _load():
    from gaphor.diagram.profiles import (
        extensionconnect,
        metaclasseditor,
        stereotypepage,
    )


_load()
