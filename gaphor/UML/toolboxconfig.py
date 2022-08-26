from gaphor import UML
from gaphor.core import gettext
from gaphor.UML.recipes import owner_package


def named_element_config(new_item, name=None):
    new_item.subject.name = gettext("New {name}").format(
        name=name or gettext(type(new_item.subject).__name__)
    )


def default_namespace(new_item):
    assert isinstance(
        new_item.subject, (UML.Type, UML.Package)
    ), f"{new_item.subject} is not a Type or Package"
    new_item.subject.package = owner_package(new_item.diagram)


def namespace_config(new_item, name=None):
    named_element_config(new_item, name)
    default_namespace(new_item)
