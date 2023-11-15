"""Gaphor file reader.

This module contains only one interesting function:

    parse(filename)

which returns a dictionary of ID -> <parsed_object> pairs.

A parsed_object contains values and references. values is a dictionary of
name -> value pairs. A value contains a string with the value read from the
model file. The references contain a list of name -> reference_list pairs, where
reference_list is a list of ID's.

Each element has a type, which corresponds to a class name in one of the
ModelingLanguage modules. Elements also have a unique ID, by which they are
referered to in the dictionary returned by parse().

The generator parse_generator(filename, loader) may be used if the loading
takes a long time. The yielded values are the percentage of the file read.
"""

from __future__ import annotations

import logging
import os
from collections import OrderedDict
from xml.sax import SAXParseException, handler, xmlreader

from defusedxml.sax import make_parser

from gaphor.core.modeling import Element
from gaphor.storage.upgrade_canvasitem import upgrade_canvasitem

__all__ = ["parse", "ParserException"]

log = logging.getLogger(__name__)


class base:
    """Simple base class for element, and canvas."""

    def __init__(self):
        self.values: dict[str, str] = {}
        self.references: dict[str, str | list[str]] = {}

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError as e:
            raise AttributeError(e) from e

    def __getitem__(self, key):
        try:
            return self.values[key]
        except KeyError:
            return self.references[key]

    def get(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            return None


class element(base):
    def __init__(self, id: str, type: str, canvas: canvas | None = None):
        base.__init__(self)
        self.id = id
        self.type = type
        self.element: Element | None = None


class canvas(base):
    pass


XMLNS = "http://gaphor.sourceforge.net/model"


class ParserException(Exception):
    pass


class MergeConflictDetected(Exception):
    pass


# Loader state:
[
    ROOT,  # Expect 'gaphor' element
    GAPHOR,  # Expect UML classes (tag name is the UML class name)
    ELEMENT,  # Expect properties of UML object
    DIAGRAM,  # Expect properties of Diagram object + canvas
    CANVAS,  # Expect canvas properties + <item> (Gaphor < 2.5)
    ITEM,  # Expect item attributes and nested items (Gaphor < 2.5)
    ATTR,  # Reading contents of an attribute (such as a <val> or <ref>)
    VAL,  # Redaing contents of a <val> tag
    REFLIST,  # In a <reflist>
    REF,  # Reading contents of a <ref> tag
] = range(10)

State = int


class GaphorLoader(handler.ContentHandler):
    """Create a list of elements.

    an element may contain a canvas and a canvas may contain canvas
    items. Each element can have values and references to other
    elements.
    """

    def __init__(self):
        handler.ContentHandler.__init__(self)
        self.version = None
        self.gaphor_version = ""
        self.startDocument()

    def push(self, element, state):
        """Add an element to the item stack."""
        self._stack.append((element, state))

    def pop(self):
        """Return the last item on the stack.

        The item is removed from the stack.
        """
        return self._stack.pop()[0]

    def peek(self, depth=1):
        """Return the last item on the stack.

        The item is not removed.
        """
        return self._stack[-1 * depth][0]

    def state(self):
        """Return the current state of the parser."""
        try:
            return self._stack[-1][1]
        except IndexError:
            return ROOT

    def startDocument(self):
        """Start of document: all our attributes are initialized."""
        self.version = None
        self.gaphor_version = ""
        self.elements: dict[str, element] = OrderedDict()
        self._stack: list[tuple[element | canvas, State]] = []
        self.text = ""
        self._start_element_handlers = (
            self.start_element,
            self.start_canvas,
            self.start_canvas_item,
            self.start_attribute,
            self.start_reference,
            self.start_attribute_value,
            self.start_root,
            self.invalid_tag,
        )

    def endDocument(self):
        if len(self._stack) != 0:
            raise ParserException("Invalid XML document.")

    def startElement(self, name, attrs):
        self.text = ""

        state = self.state()

        for h in self._start_element_handlers:
            if h(state, name, attrs):
                break

    def start_element(self, state, name, attrs):
        # Read an element class. The name of the tag is the class name:
        if state == GAPHOR:
            if "id" not in attrs:
                log.exception(f"File corrupt: Element {name} has no id")
            id = attrs["id"]
            e = element(id, name)
            if id in self.elements.keys():
                log.exception(
                    f"File corrupt: duplicate element. Remove element {name} with id {id} and try again"
                )
            self.elements[id] = e
            self.push(e, name == "Diagram" and DIAGRAM or ELEMENT)
            return True

    def start_canvas(self, state, name, attrs):
        # NB. Only used for pre-2.5 models.
        # Special treatment for the <canvas> tag in a Diagram:
        if state == DIAGRAM and name == "canvas":
            c = canvas()
            self.push(c, CANVAS)
            return True

    def start_canvas_item(self, state, name, attrs):
        # NB. Only used for pre-2.5 models.
        # Items in a canvas are referenced by the <item> tag:
        if state in (CANVAS, ITEM) and name == "item":
            id = attrs["id"]
            ci = element(id, attrs["type"])
            assert id not in self.elements.keys(), f"{id} already defined"
            parent_or_canvas = self.peek()
            if state == ITEM:
                ci.references["parent"] = parent_or_canvas.id
                ci.references["diagram"] = parent_or_canvas.references["diagram"]
            else:
                ci.references["diagram"] = self.peek(2).id
            self.elements[id] = ci
            self.push(ci, ITEM)
            return True

    def start_attribute(self, state, name, attrs):
        # Store the attribute name on the stack, so we can use it later
        # to store the <ref>, <reflist> or <val> content:
        if state in (ELEMENT, DIAGRAM, CANVAS, ITEM):
            # handle 'normal' attributes
            self.push(name, ATTR)
            return True

    def start_reference(self, state, name, attrs):
        # Reference list:
        if state == ATTR and name == "reflist":
            self.push(self.peek(), REFLIST)
            return True

        # Reference with multiplicity 1:
        elif state == ATTR and name == "ref":
            n = self.peek()
            self.peek(2).references[n] = attrs["refid"]
            self.push(None, REF)
            return True

        # Reference with multiplicity *:
        elif state == REFLIST and name == "ref":
            n = self.peek()
            # Fetch the element instance from the stack
            r = self.peek(3).references
            refid = attrs["refid"]
            try:
                r[n].append(refid)
            except KeyError:
                r[n] = [refid]
            self.push(None, REF)
            return True

    def start_attribute_value(self, state, name, attrs):
        # We need to get the text within the <val> tag:
        if state == ATTR and name == "val":
            self.push(None, VAL)
            return True

    def start_root(self, state, name, attrs):
        # The <gaphor> tag is the toplevel tag:
        if state == ROOT and name == "gaphor":
            assert attrs["version"] == "3.0"
            self.version = attrs["version"]
            self.gaphor_version = attrs.get("gaphor-version") or attrs.get(
                "gaphor_version"
            )
            self.push(None, GAPHOR)
            return True

    def invalid_tag(self, state, name, attrs):
        raise ParserException(f"Invalid XML: tag <{name}> not known (state = {state})")

    def endElement(self, name):
        # Put the text on the value
        if self.state() == VAL:
            # Two levels up: the attribute name
            n = self.peek(2)
            # Three levels up: the element instance
            self.peek(3).values[n] = self.text
        elif self.state() == ITEM:
            item = self.pop()
            new_canvasitems = upgrade_canvasitem(item, self.gaphor_version)
            for new_item in new_canvasitems:
                self.elements[new_item.id] = new_item
            return
        self.pop()

    def startElementNS(self, name, qname, attrs):
        if not name[0] or name[0] == XMLNS:
            a = {key[1]: val for key, val in list(attrs.items())}
            self.startElement(name[1], a)

    def endElementNS(self, name, qname):
        if not name[0] or name[0] == XMLNS:
            self.endElement(name[1])

    def characters(self, content):
        """Read characters."""
        self.text = self.text + content


def parse(filename) -> dict[str, element]:
    """Parse a file and return a dictionary ID:element."""
    loader = GaphorLoader()

    for _ in parse_generator(filename, loader):
        pass
    return loader.elements


class ErrorHandler(handler.ErrorHandler):
    def error(self, exception):
        raise exception from None

    def fatalError(self, exception):
        raise exception from None

    def warning(self, exception):
        log.warning(exception)


def parse_generator(file_obj, loader):
    """The generator based version of parse().

    parses the file and load it with ContentHandler loader. Returns a
    progress percentage.
    """
    assert file_obj.seekable()
    assert isinstance(loader, GaphorLoader), "loader should be a GaphorLoader"

    parser = new_parser(loader)
    file_size = get_file_size(file_obj)
    count = 0

    for line in file_obj:
        try:
            parser.feed(line)
        except SAXParseException as e:
            if line.startswith("<<<<<"):
                raise MergeConflictDetected from e
            raise
        count += len(line)
        yield (count * 100) / file_size


def new_parser(loader):
    parser = make_parser()
    assert isinstance(parser, xmlreader.IncrementalParser)

    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(loader)
    parser.setErrorHandler(ErrorHandler())
    return parser


def get_file_size(file_obj):
    orig_pos = file_obj.tell()
    file_size = file_obj.seek(0, os.SEEK_END)
    file_obj.seek(orig_pos)
    return file_size
