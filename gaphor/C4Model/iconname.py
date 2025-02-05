from gaphor.C4Model.c4model import Container, Database, Dependency, Person
from gaphor.diagram.iconname import icon_name


@icon_name.register(Container)
def get_name_for_class(element):
    if element.type == "Software System":
        return "gaphor-c4-software-system-symbolic"
    elif element.type == "Component":
        return "gaphor-c4-component-symbolic"
    return "gaphor-c4-container-symbolic"


@icon_name.register(Database)
def get_database_name(_element):
    return "gaphor-c4-database-symbolic"


@icon_name.register(Dependency)
def get_dependency_name(_element):
    return "gaphor-dependency-symbolic"


@icon_name.register(Person)
def get_person_name(_element):
    return "gaphor-c4-person-symbolic"
