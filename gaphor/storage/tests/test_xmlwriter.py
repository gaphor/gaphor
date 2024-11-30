import sys

import pytest

from gaphor.storage.xmlwriter import XMLWriter


class Writer:
    def __init__(self):
        self.s = ""

    def write(self, text):
        self.s += text


def test_elements_1():
    w = Writer()
    xml_w = XMLWriter(w)
    with xml_w.document():
        with xml_w.element("foo", {}):
            pass

    xml = f"""<?xml version="1.0" encoding="{sys.getdefaultencoding()}"?>\n<foo/>"""
    assert w.s == xml, f"{w.s} != {xml}"


def test_elements_2():
    w = Writer()
    xml_w = XMLWriter(w)
    with xml_w.document():
        with xml_w.element("foo", {}):
            with xml_w.element("bar", {}):
                pass

    xml = f"""<?xml version="1.0" encoding="{sys.getdefaultencoding()}"?>\n<foo>\n<bar/>\n</foo>"""
    assert w.s == xml, w.s


def test_elements_test():
    w = Writer()
    xml_w = XMLWriter(w)
    with xml_w.document():
        with xml_w.element("foo", {}):
            with xml_w.element("bar", {}):
                xml_w.characters("hello")

    xml = f"""<?xml version="1.0" encoding="{sys.getdefaultencoding()}"?>\n<foo>\n<bar>hello</bar>\n</foo>"""
    assert w.s == xml, w.s


def test_elements_ns_default():
    w = Writer()
    xml_w = XMLWriter(w)
    with xml_w.document():
        xml_w.prefix_mapping(None, "http://gaphor.devjavu.com/schema")
        with xml_w.element_ns(("http://gaphor.devjavu.com/schema", "foo"), {}):
            pass

    xml = f"""<?xml version="1.0" encoding="{sys.getdefaultencoding()}"?>\n<foo xmlns="http://gaphor.devjavu.com/schema"/>"""
    assert w.s == xml, w.s


def test_elements_ns_1():
    w = Writer()
    xml_w = XMLWriter(w)
    with xml_w.document():
        xml_w.prefix_mapping("g", "http://gaphor.devjavu.com/schema")
        with xml_w.element_ns(("http://gaphor.devjavu.com/schema", "foo"), {}):
            pass

    xml = f"""<?xml version="1.0" encoding="{sys.getdefaultencoding()}"?>\n<g:foo xmlns:g="http://gaphor.devjavu.com/schema"/>"""
    assert w.s == xml, w.s


def test_prefix_mappings():
    w = Writer()
    with XMLWriter(w).document() as xml_w:
        xml_w.prefix_mapping("example", "http://example.com/schema")
        with xml_w.element_ns(("http://example.com/schema", "foo"), {}):
            with xml_w.element_ns(("http://example.com/schema", "bar"), {}):
                pass

        with pytest.raises(KeyError):
            with xml_w.element_ns(("http://example.com/schema", "foo"), {}):
                pass
