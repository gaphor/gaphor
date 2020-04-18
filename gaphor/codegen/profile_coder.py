"""Parse a SysML Gaphor Model and generate a SysML data model."""

from typing import List

from gaphor import UML
from gaphor.application import Session
from gaphor.codegen import override
from gaphor.codegen.writer import Writer
from gaphor.storage import storage


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
    comments: List = element_factory.lselect(lambda e: e.isKindOf(UML.Comment))
    overrides = override.Overrides(overridesfile)
    writer = Writer(overrides)
    for comment in comments:
        writer.add_comment(comment)

    writer.write(outfile, "")
    element_factory.shutdown()
    session.shutdown()
