import io
import textwrap
from xml.sax import SAXParseException

import pytest

from gaphor.storage import storage
from gaphor.storage.parser import MergeConflictDetected, ParserException


def buffer(text):
    file = io.StringIO()
    file.write(textwrap.dedent(text))
    file.seek(0)
    return file


def test_load_model(element_factory, modeling_language):
    file = buffer(
        """\
        <?xml version="1.0" encoding="utf-8"?>
        <gaphor xmlns="http://gaphor.sourceforge.net/model" version="3.0" gaphor-version="2.12.1">
          <StyleSheet id="58d6989a-66f8-11ec-b4c8-0456e5e540ed" />
          <Diagram id="58d6c536-66f8-11ec-b4c8-0456e5e540ed">
            <name>
              <val>main</val>
            </name>
          </Diagram>
        </gaphor>
        """
    )

    storage.load(file, element_factory, modeling_language)

    assert element_factory.lselect()


def test_load_model_with_unknown_element(element_factory, modeling_language):
    file = buffer(
        """\
        <?xml version="1.0" encoding="utf-8"?>
        <gaphor xmlns="http://gaphor.sourceforge.net/model" version="3.0" gaphor-version="2.12.1">
          <StyleSheet id="58d6989a-66f8-11ec-b4c8-0456e5e540ed" />
          <FooBar id="58d6989a-66f8-11ec-b4c8-0456e5e540ed" />
        </gaphor>
        """
    )

    with pytest.raises(storage.UnknownModelElementError):
        storage.load(file, element_factory, modeling_language)

    assert not element_factory.lselect()


def test_plain_text(element_factory, modeling_language):
    file = buffer(
        """\
        Hello world
        """
    )

    with pytest.raises(SAXParseException):
        storage.load(file, element_factory, modeling_language)

    assert not element_factory.lselect()


def test_wrong_tag(element_factory, modeling_language):
    file = buffer(
        """\
        <?xml version="1.0" encoding="utf-8"?>
        <not-gaphor xmlns="http://gaphor.sourceforge.net/model" version="3.0">
          <FooBar id="58d6989a-66f8-11ec-b4c8-0456e5e540ed" />
        </not-gaphor>
        """
    )

    with pytest.raises(ParserException):
        storage.load(file, element_factory, modeling_language)

    assert not element_factory.lselect()


def test_xml_not_gaphor(element_factory, modeling_language):
    file = buffer(
        """\
        <?xml version="1.0" encoding="utf-8"?>
        <html>
          <p id="58d6989a-66f8-11ec-b4c8-0456e5e540ed">Hello</p>
        </html>
        """
    )

    with pytest.raises(ParserException):
        storage.load(file, element_factory, modeling_language)

    assert not element_factory.lselect()


def test_detect_merge_conflict(element_factory, modeling_language):
    file = buffer(
        """\
        <?xml version="1.0" encoding="utf-8"?>
        <gaphor xmlns="http://gaphor.sourceforge.net/model" version="3.0" gaphor-version="2.12.1">
        <StyleSheet id="58d6989a-66f8-11ec-b4c8-0456e5e540ed" />
        <Diagram id="58d6c536-66f8-11ec-b4c8-0456e5e540ed">
          <name>
        <<<<<<< HEAD
            <val>old</val>
        =======
            <val>new</val>
        >>>>>>> 12345678 (incoming change)
            <val>main</val>
          </name>
        </Diagram>
        </gaphor>
        """
    )

    with pytest.raises(MergeConflictDetected):
        storage.load(file, element_factory, modeling_language)

    assert not element_factory.lselect()
