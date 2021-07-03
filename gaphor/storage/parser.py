"""Gaphor file reader.

This module contains only one interesting function:

    parse(filename)

which returns a dictionary of ID -> <parsed_object> pairs.

A parsed_object contains values and references. values is a dictionary of
name -> value pairs. A value contains a string with the value read from the
model file. references contains a list of name -> reference_list pairs, where
reference_list is a list of ID's.

Each element has a type, which corresponds to a class name in one of the
ModelingLanguage modules. Elements also have a unique ID, by which they are
referered to in the dictionary returned by parse().

The generator parse_generator(filename, loader) may be used if the loading
takes a long time. The yielded values are the percentage of the file read.
"""

from __future__ import annotations

import io
import logging
import os
from collections import OrderedDict
from typing import IO
from xml.sax import handler

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
            raise AttributeError(e)

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
        self.element: object = None


class canvas(base):
    pass


XMLNS = "http://gaphor.sourceforge.net/model"


class ParserException(Exception):
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
        # make sure all variables are initialized:
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
        self.gaphor_version = None
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
            n = self.peek(1)
            self.peek(2).references[n] = attrs["refid"]
            self.push(None, REF)
            return True

        # Reference with multiplicity *:
        elif state == REFLIST and name == "ref":
            n = self.peek(1)
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
            assert attrs["version"] in ("3.0",)
            self.version = attrs["version"]
            self.gaphor_version = attrs.get("gaphor-version")
            if not self.gaphor_version:
                self.gaphor_version = attrs.get("gaphor_version")
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


def parse_generator(filename, loader):
    """The generator based version of parse().

    parses the file filename and load it with ContentHandler loader.
    """
    assert isinstance(loader, GaphorLoader), "loader should be a GaphorLoader"
    from xml.sax import make_parser

    parser = make_parser()

    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(loader)

    yield from parse_file(filename, parser)


class ProgressGenerator:
    """A generator that yields the progress of taking from a file input object
    and feeding it into an output object.

    The supplied file object is neither opened not closed by this
    generator.  The file object is assumed to already be opened for
    reading and that it will be closed elsewhere.
    """

    def __init__(self, input, output, block_size=512):
        """Initialize the progress generator.

        The input parameter is a file object.  The output parameter is
        usually a SAX parser but can be anything that implements a
        feed() method.  The block size is the size of each block that is
        read from the input.
        """

        self.input = input
        self.output = output
        self.block_size = block_size
        if isinstance(self.input, io.IOBase):
            orig_pos = self.input.tell()
            self.file_size = self.input.seek(0, 2)
            self.input.seek(orig_pos, os.SEEK_SET)
        elif isinstance(self.input, str):
            self.file_size = len(self.input)

    def __iter__(self):
        """Return a generator that yields the progress of reading data from the
        input and feeding it into the output.

        The progress yielded in each iteration is the percentage of data
        read, relative to the to input file size.
        """

        block = self.input.read(self.block_size)
        read_size = len(block)

        while block:
            self.output.feed(block)
            block = self.input.read(self.block_size)
            read_size += len(block)
            yield (read_size * 100) / self.file_size


def parse_file(filename, parser):
    """Parse the supplied file using the supplied parser.

    The parser parameter should be a GaphorLoader instance.  The
    filename parameter can be an open file descriptor instance or the
    name of a file.  The progress percentage of the parser is yielded.
    """

    is_fd = True

    if isinstance(filename, io.IOBase):
        file_obj: IO | io.IOBase = filename
    else:
        is_fd = False
        file_obj = open(filename, "r")

    try:
        yield from ProgressGenerator(file_obj, parser)
    finally:
        parser.close()

        if not is_fd:
            file_obj.close()
