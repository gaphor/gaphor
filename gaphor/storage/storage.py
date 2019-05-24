"""
Load and save Gaphor models to Gaphors own XML format.

Three functions are exported:
load(filename)
    load a model from a file
save(filename)
    store the current model in a file
"""

__all__ = ["load", "save"]

import gc
import logging
import os.path
import io

import gaphas

from gaphor import UML
from gaphor import diagram
from gaphor.UML.collection import collection
from gaphor.application import Application, NotInitializedError
from gaphor.i18n import _
from gaphor.storage import parser, diagramitems


FILE_FORMAT_VERSION = "3.0"
NAMESPACE_MODEL = "http://gaphor.sourceforge.net/model"

log = logging.getLogger(__name__)


def save(writer=None, factory=None, status_queue=None):
    for status in save_generator(writer, factory):
        if status_queue:
            status_queue(status)


def save_generator(writer, factory):
    """
    Save the current model using @writer, which is a
    gaphor.misc.xmlwriter.XMLWriter instance.
    """

    # Maintain a set of id's, one for elements, one for references.
    # Write only to file if references is a subset of elements

    def save_reference(name, value):
        """
        Save a value as a reference to another element in the model.
        This applies to both UML as well as canvas items.
        """
        # Save a reference to the object:
        if value.id:
            writer.startElement(name, {})
            writer.startElement("ref", {"refid": value.id})
            writer.endElement("ref")
            writer.endElement(name)

    def save_collection(name, value):
        """
        Save a list of references.
        """
        if len(value) > 0:
            writer.startElement(name, {})
            writer.startElement("reflist", {})
            for v in value:
                # save_reference(name, v)
                if v.id:
                    writer.startElement("ref", {"refid": v.id})
                    writer.endElement("ref")
            writer.endElement("reflist")
            writer.endElement(name)

    def save_value(name, value):
        """
        Save a value (attribute).
        """
        if value is not None:
            writer.startElement(name, {})
            writer.startElement("val", {})
            if isinstance(value, str):
                writer.characters(value)
            elif isinstance(value, bool):
                # Write booleans as 0/1.
                writer.characters(str(int(value)))
            else:
                writer.characters(str(value))
            writer.endElement("val")
            writer.endElement(name)

    def save_element(name, value):
        """
        Save attributes and references from items in the gaphor.UML module.
        A value may be a primitive (string, int), a gaphor.UML.collection
        (which contains a list of references to other UML elements) or a
        gaphas.Canvas (which contains canvas items).
        """
        # log.debug('saving element: %s|%s %s' % (name, value, type(value)))
        if isinstance(value, (UML.Element, gaphas.Item)):
            save_reference(name, value)
        elif isinstance(value, collection):
            save_collection(name, value)
        elif isinstance(value, gaphas.Canvas):
            writer.startElement("canvas", {})
            value.save(save_canvasitem)
            writer.endElement("canvas")
        else:
            save_value(name, value)

    def save_canvasitem(name, value, reference=False):
        """
        Save attributes and references in a gaphor.diagram.* object.
        The extra attribute reference can be used to force UML
        """
        # log.debug('saving canvasitem: %s|%s %s' % (name, value, type(value)))
        if isinstance(value, collection) or (
            isinstance(value, (list, tuple)) and reference == True
        ):
            save_collection(name, value)
        elif reference:
            save_reference(name, value)
        elif isinstance(value, gaphas.Item):
            writer.startElement(
                "item", {"id": value.id, "type": value.__class__.__name__}
            )
            value.save(save_canvasitem)

            # save subitems
            for child in value.canvas.get_children(value):
                save_canvasitem(None, child)

            writer.endElement("item")

        elif isinstance(value, UML.Element):
            save_reference(name, value)
        else:
            save_value(name, value)

    writer.startDocument()
    writer.startPrefixMapping("", NAMESPACE_MODEL)
    writer.startElementNS(
        (NAMESPACE_MODEL, "gaphor"),
        None,
        {
            (NAMESPACE_MODEL, "version"): FILE_FORMAT_VERSION,
            (NAMESPACE_MODEL, "gaphor-version"): Application.distribution.version,
        },
    )

    size = factory.size()
    n = 0
    for e in list(factory.values()):
        clazz = e.__class__.__name__
        assert e.id
        writer.startElement(clazz, {"id": str(e.id)})
        e.save(save_element)
        writer.endElement(clazz)

        n += 1
        if n % 25 == 0:
            yield (n * 100) / size

    # writer.endElement('gaphor')
    writer.endElementNS((NAMESPACE_MODEL, "gaphor"), None)
    writer.endPrefixMapping("")
    writer.endDocument()


def load_elements(elements, factory, status_queue=None):
    for status in load_elements_generator(elements, factory):
        if status_queue:
            status_queue(status)


def load_elements_generator(elements, factory, gaphor_version=None):
    """
    Load a file and create a model if possible.
    Exceptions: IOError, ValueError.
    """
    # TODO: restructure loading code, first load model, then add canvas items
    log.debug(_("Loading %d elements...") % len(elements))

    # The elements are iterated three times:
    size = len(elements) * 3

    def update_status_queue(_n=[0]):
        n = _n[0] = _n[0] + 1
        if n % 30 == 0:
            return (n * 100) / size

    # First create elements and canvas items in the factory
    # The elements are stored as attribute 'element' on the parser objects:

    def create_canvasitems(canvas, canvasitems, parent=None):
        """
        Canvas is a read gaphas.Canvas, items is a list of parser.canvasitem's
        """
        for item in canvasitems:
            item = upgrade_canvas_item_to_1_1_0(item)
            cls = getattr(diagramitems, item.type)
            item.element = diagram.create_as(cls, item.id)
            canvas.add(item.element, parent=parent)
            assert canvas.get_parent(item.element) is parent
            create_canvasitems(canvas, item.canvasitems, parent=item.element)

    for id, elem in list(elements.items()):
        st = update_status_queue()
        if st:
            yield st
        if isinstance(elem, parser.element):
            cls = getattr(UML, elem.type)
            # log.debug('Creating UML element for %s (%s)' % (elem, elem.id))
            elem.element = factory.create_as(cls, id)
            if elem.canvas is not None:
                elem.element.canvas.block_updates = True
                create_canvasitems(elem.element.canvas, elem.canvas.canvasitems)
        elif not isinstance(elem, parser.canvasitem):
            raise ValueError(
                'Item with id "%s" and type %s can not be instantiated'
                % (id, type(elem))
            )

    # load attributes and create references:
    for id, elem in list(elements.items()):
        st = update_status_queue()
        if st:
            yield st
        # Ensure that all elements have their element instance ready...
        assert hasattr(elem, "element")

        # load attributes and references:
        for name, value in list(elem.values.items()):
            try:
                elem.element.load(name, value)
            except:
                log.error(
                    "Loading value %s (%s) for element %s failed."
                    % (name, value, elem.element)
                )
                raise

        for name, refids in list(elem.references.items()):
            if isinstance(refids, list):
                for refid in refids:
                    try:
                        ref = elements[refid]
                    except:
                        raise ValueError(
                            "Invalid ID for reference (%s) for element %s.%s"
                            % (refid, elem.type, name)
                        )
                    else:
                        try:
                            elem.element.load(name, ref.element)
                        except:
                            log.error(
                                "Loading %s.%s with value %s failed"
                                % (type(elem.element).__name__, name, ref.element.id)
                            )
                            raise
            else:
                try:
                    ref = elements[refids]
                except:
                    raise ValueError("Invalid ID for reference (%s)" % refids)
                else:
                    try:
                        elem.element.load(name, ref.element)
                    except:
                        log.error(
                            "Loading %s.%s with value %s failed"
                            % (type(elem.element).__name__, name, ref.element.id)
                        )
                        raise

    # Before version 0.7.2 there was only decision node (no merge nodes).
    # This node could have many incoming and outgoing flows (edges).
    # According to UML specification decision node has no more than one
    # incoming node.
    #
    # Now, we have implemented merge node, which can have many incoming
    # flows. We also support combining of decision and merge nodes as
    # described in UML specification.
    #
    # Data model, loaded from file, is updated automatically, so there is
    # no need for special function.

    for d in factory.select(lambda e: isinstance(e, UML.Diagram)):
        # update_now() is implicitly called when lock is released
        d.canvas.block_updates = False

    # do a postload:
    for id, elem in list(elements.items()):
        st = update_status_queue()
        if st:
            yield st
        elem.element.postload()


def load(filename, factory, status_queue=None):
    """
    Load a file and create a model if possible.
    Optionally, a status queue function can be given, to which the
    progress is written (as status_queue(progress)).
    """
    for status in load_generator(filename, factory):
        if status_queue:
            status_queue(status)


def load_generator(filename, factory):
    """
    Load a file and create a model if possible.
    This function is a generator. It will yield values from 0 to 100 (%)
    to indicate its progression.
    """
    if isinstance(filename, io.IOBase):
        log.info("Loading file from file descriptor")
    else:
        log.info("Loading file %s" % os.path.basename(filename))
    try:
        # Use the incremental parser and yield the percentage of the file.
        loader = parser.GaphorLoader()
        for percentage in parser.parse_generator(filename, loader):
            pass
            if percentage:
                yield percentage / 2
            else:
                yield percentage
        elements = loader.elements
        gaphor_version = loader.gaphor_version

    except Exception as e:
        log.error("File could no be parsed", exc_info=True)
        raise

    if version_lower_than(gaphor_version, (0, 17, 0)):
        raise ValueError(
            "Gaphor model version should be at least 0.17.0 (found {})".format(
                gaphor_version
            )
        )

    log.info("Read %d elements from file" % len(elements))

    factory.flush()
    gc.collect()
    with factory.block_events():
        try:
            for percentage in load_elements_generator(
                elements, factory, gaphor_version
            ):
                if percentage:
                    yield percentage / 2 + 50
                else:
                    yield percentage
            gc.collect()
            yield 100
        except Exception as e:
            log.warning("file %s could not be loaded" % filename, e)
            raise
    factory.notify_model()


def version_lower_than(gaphor_version, version):
    """
    if version_lower_than('0.3.0', (0, 15, 0)):
       ...
    """
    parts = gaphor_version.split(".")
    try:
        return tuple(map(int, parts)) < version
    except ValueError:
        # We're having a -dev, -pre, -beta, -alpha or whatever version
        parts = parts[:-1]
        return tuple(map(int, parts)) <= version


def upgrade_canvas_item_to_1_1_0(item):
    if item.type == "MetaclassItem":
        item.type = "ClassItem"
    return item
