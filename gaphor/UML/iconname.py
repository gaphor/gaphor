from gaphor.diagram.iconname import get_default_icon_name, get_icon_name, to_kebab_case
from gaphor.UML import uml as UML


@get_icon_name.register(UML.Class)
def get_name_for_class(element):
    if element.extension:
        return "gaphor-metaclass-symbolic"
    else:
        return get_default_icon_name(element)


@get_icon_name.register(UML.Pseudostate)
def get_name_for_pseudostate(element):
    return f"gaphor-{to_kebab_case(element.kind or 'initial')}-pseudostate-symbolic"
