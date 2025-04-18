"""Save Gaphor models to Gaphors own XML format."""

__all__ = ["save"]

import logging
from collections.abc import Callable, Iterable
from functools import partial

from gaphor import application
from gaphor.core.modeling import Base, ElementFactory
from gaphor.core.modeling.collection import collection
from gaphor.storage.xmlwriter import WriterProtocol, XMLWriter

FILE_FORMAT_VERSION = "4"
MODEL_NS = "https://gaphor.org/model"
MODELING_LANGUAGE_NS = "https://gaphor.org/modelinglanguage"

log = logging.getLogger(__name__)


def save(
    out: WriterProtocol,
    element_factory: ElementFactory,
    status_queue: Callable[[float], None] | None = None,
):
    for status in save_generator(out, element_factory):
        if status_queue:
            status_queue(status)


def save_generator(
    out: WriterProtocol, element_factory: ElementFactory
) -> Iterable[float]:
    """Save the current model using @writer, which is a
    gaphor.storage.xmlwriter.XMLWriter instance."""

    with XMLWriter(out).document() as writer:
        writer.prefix_mapping("", MODEL_NS)
        for ml in sorted({e.__modeling_language__ for e in element_factory}):
            writer.prefix_mapping(ml, f"{MODELING_LANGUAGE_NS}/{ml}")

        with writer.element_ns(
            (MODEL_NS, "gaphor"),
            {
                (MODEL_NS, "version"): FILE_FORMAT_VERSION,
                (MODEL_NS, "gaphor-version"): application.distribution().version,
            },
        ):
            with writer.element_ns((MODEL_NS, "model"), {}):
                size = element_factory.size()
                save_func = partial(
                    save_element, element_factory=element_factory, writer=writer
                )
                for n, e in enumerate(element_factory, start=1):
                    clazz = e.__class__.__name__
                    assert e.id
                    ns = f"{MODELING_LANGUAGE_NS}/{e.__modeling_language__}"
                    with writer.element_ns((ns, clazz), {(MODEL_NS, "id"): str(e.id)}):
                        e.save(save_func)

                    if n % 25 == 0:
                        yield (n * 100) / size


def save_element(
    name: str,
    value: str | int | bool | Base | collection[Base],
    element_factory: ElementFactory,
    writer: XMLWriter,
) -> None:
    """Save attributes and references from items in the gaphor.UML module.

    A value may be a primitive (string, int), a
    gaphor.core.modeling.collection (which contains a list of references
    to other UML elements) or a Diagram (which contains diagram items).
    """

    def resolvable(value):
        if value.id and value in element_factory:
            return True
        log.warning(
            f"Model has unknown reference {value.id}. Reference will be skipped."
        )
        return False

    def save_reference(name: str, value: Base):
        """Save a value as a reference to another element in the model.

        This applies to both UML and canvas items.
        """
        if resolvable(value):
            with writer.element(name, {}):
                with writer.element("ref", {"refid": value.id}):
                    pass

    def save_collection(name: str, value: collection[Base]):
        """Save a list of references."""
        if value:
            with writer.element(name, {}):
                with writer.element("reflist", {}):
                    for v in value:
                        if resolvable(v):
                            with writer.element("ref", {"refid": v.id}):
                                pass

    def save_value(name: str, value: str | int | bool):
        """Save a value (attribute)."""
        if value is not None:
            with writer.element(name, {}):
                with writer.element("val", {}):
                    writer.characters(str(value))

    if isinstance(value, Base):
        save_reference(name, value)
    elif isinstance(value, collection):
        save_collection(name, value)
    else:
        save_value(name, value)
