from gaphor.ui.iconname import get_default_icon_name, get_icon_name
from gaphor.UML import uml as UML


@get_icon_name.register(UML.Class)
def get_name_for_class(element):
    if element.extension:
        return "gaphor-metaclass-symbolic"
    else:
        return get_default_icon_name(element)


@get_icon_name.register(UML.Property)
def get_name_for_property(element):
    if element.association:
        return "gaphor-association-symbolic"
    else:
        return "gaphor-property-symbolic"
