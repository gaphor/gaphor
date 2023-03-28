from gaphor.UML.recipes import owner_package


def named_element_config(new_item, name=None):
    new_item.subject.name = new_item.diagram.gettext("New {name}").format(
        name=name or new_item.diagram.gettext(type(new_item.subject).__name__)
    )


def default_namespace(new_item):
    if not new_item.subject.namespace:
        new_item.subject.package = owner_package(new_item.diagram)


def namespace_config(new_item, name=None):
    named_element_config(new_item, name)
    default_namespace(new_item)
