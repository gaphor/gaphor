import gaphor.UML.uml as UML
from gaphor.ui.iconname import get_icon_name


@get_icon_name.register(UML.Class)
def get_name_for_class(element):
    if isinstance(element, UML.Stereotype):
        return "gaphor-stereotype-symbolic"
    elif element.extension:
        return "gaphor-metaclass-symbolic"
    else:
        return "gaphor-class-symbolic"


@get_icon_name.register(UML.Property)
def get_name_for_property(element):
    if element.association:
        return "gaphor-association-symbolic"
    else:
        return "gaphor-property-symbolic"
