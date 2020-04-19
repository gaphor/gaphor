"""Parse a SysML Gaphor Model and generate a SysML data model."""

from typing import List, Set

from gaphor import UML
from gaphor.application import Session
from gaphor.storage import storage


def kind_of(factory, cls):
    """Find UML metaclass instances using element factory."""

    return factory.lselect(lambda e: e.isKindOf(cls))


def generate(filename, outfile=None, overridesfile=None):
    services = [
        "element_dispatcher",
        "event_manager",
        "component_registry",
        "element_factory",
        "modeling_language",
    ]
    session = Session(services=services)
    element_factory = session.get_service("element_factory")
    modeling_language = session.get_service("modeling_language")
    with open(filename):
        storage.load(
            filename, factory=element_factory, modeling_language=modeling_language,
        )
    classes: List = kind_of(element_factory, UML.Class)

    with open(outfile, "w") as f:
        klass_names: Set = set()
        for klass in classes:
            name = klass.name
            if name not in klass_names and name[0] != "~":
                f.write(f"class {name}:\n")
                f.write("    pass\n\n")
                klass_names.add(name)

    element_factory.shutdown()
    session.shutdown()
