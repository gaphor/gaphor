from gaphor.diagram.profiles.extension import ExtensionItem
from gaphor.diagram.profiles.packageimport import PackageImportItem


def _load():
    from gaphor.diagram.profiles import (
        extensionconnect,
        metaclasspropertypage,
        packageimportconnect,
        stereotypepropertypages,
    )


_load()
