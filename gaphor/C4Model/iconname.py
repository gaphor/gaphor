from gaphor.C4Model.c4model import Container, Database, Dependency
from gaphor.diagram.iconname import get_default_icon_name, icon_name


@icon_name.register(Container)
def get_name_for_class(element):
    if element.type == "Software System":
        return "gaphor-c4-software-system-symbolic"
    elif element.type == "Component":
        return "gaphor-c4-component-symbolic"
    return get_default_icon_name(element)


@icon_name.register(Database)
def get_database_name(element):
    return get_default_icon_name(element)


@icon_name.register(Dependency)
def get_dependency_name(element):
    return "gaphor-dependency-symbolic"
