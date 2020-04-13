from gaphor.UML.profiles.extension import ExtensionItem
from gaphor.UML.profiles.packageimport import PackageImportItem


def _load():
    from gaphor.UML.profiles import (
        extensionconnect,
        metaclasspropertypage,
        packageimportconnect,
        stereotypepropertypages,
    )


_load()
