from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Protocol
from xml.sax.saxutils import escape, quoteattr

# See whether the xmlcharrefreplace error handler is
# supported
try:
    from codecs import xmlcharrefreplace_errors

    _error_handling = "xmlcharrefreplace"
    del xmlcharrefreplace_errors
except ImportError:
    _error_handling = "strict"


class WriterProtocol(Protocol):
    def write(self, text: str):
        """Write text"""


class XMLWriter:
    def __init__(self, out: WriterProtocol, encoding="utf-8"):
        super().__init__()
        self._out = out
        self._encoding = encoding
        self._current_context: dict[str, str] = {}  # contains uri -> prefix mapping
        self._undeclared_ns_maps: list[tuple[str, str]] = []

        self._in_cdata = False
        self._in_start_tag = False
        self._next_newline = False

    def _write(self, text: str, start_tag=False, end_tag=False) -> None:
        """Write data.

        Tags should not be escaped. They should be marked by setting
        either ``start_tag`` or ``end_tag`` to ``True``. Only the tag
        should be marked this way. Other stuff, such as namespaces and
        attributes can be written directly to the file.
        """
        if not isinstance(text, str):
            text = text.decode(self._encoding, _error_handling)

        if self._next_newline:
            self._out.write("\n")
            self._next_newline = False

        if start_tag and not self._in_start_tag:
            self._in_start_tag = True
            self._out.write("<")
        elif start_tag:
            self._out.write(">")
            self._out.write("\n")
            self._out.write("<")
        elif end_tag and self._in_start_tag:
            self._out.write("/>")
            self._in_start_tag = False
            self._next_newline = True
            return
        elif self._in_start_tag:
            self._out.write(">")
            self._in_start_tag = False
        elif end_tag:
            self._out.write("</")
            self._out.write(text)
            self._out.write(">")
            self._in_start_tag = False
            self._next_newline = True
            return

        self._out.write(text)

    def _qname(self, name: tuple[str, str]) -> str:
        """Builds a qualified name from a (ns_url, localname) pair."""
        if name[0]:
            if prefix := self._current_context[name[0]]:
                # If it is not the default namespace, prepend the prefix
                return f"{prefix}:{name[1]}"
        # Return the unqualified name
        return name[1]

    @contextmanager
    def document(self) -> Iterator[XMLWriter]:
        self._write(f'<?xml version="1.0" encoding="{self._encoding}"?>\n')
        yield self

    @contextmanager
    def element_ns(
        self, name: tuple[str, str], attrs: dict[tuple[str, str], str]
    ) -> Iterator[XMLWriter]:
        with self._prefix_mappings() as xmlns:
            self._write(self._qname(name), start_tag=True)
            self._out.write(xmlns)

            for attr, value in list(attrs.items()):
                self._out.write(f" {self._qname(attr)}={quoteattr(value)}")

            yield self

            self._write(f"{self._qname(name)}", end_tag=True)

    @contextmanager
    def element(self, name: str, attrs: dict[str, str]) -> Iterator[XMLWriter]:
        """Create new element in default namespace."""
        ns = next(
            (uri for uri, prefix in self._current_context.items() if prefix == ""), ""
        )
        with self.element_ns(
            (ns, name), {(ns, name): value for name, value in attrs.items()}
        ):
            yield self

    @contextmanager
    def cdata(self) -> Iterator[XMLWriter]:
        self._write("<![CDATA[")
        self._in_cdata = True

        yield self

        self._write("]]>")
        self._in_cdata = False

    def prefix_mapping(self, prefix: str, uri: str) -> None:
        self._undeclared_ns_maps.append((prefix, uri))

    @contextmanager
    def _prefix_mappings(self) -> Iterator[str]:
        if not self._undeclared_ns_maps:
            yield ""
        else:
            current_context = self._current_context.copy()

            xmlns = ""
            for prefix, uri in self._undeclared_ns_maps:
                self._current_context[uri] = prefix
                if prefix:
                    xmlns += f' xmlns:{prefix}="{uri}"'
                else:
                    xmlns += f' xmlns="{uri}"'

            self._undeclared_ns_maps = []

            yield xmlns

            self._current_context = current_context

    def characters(self, content: str) -> None:
        if self._in_cdata:
            self._write(content.replace("]]>", "] ]>"))
        else:
            self._write(escape(content))

    def processing_instruction(self, target: str, data: str) -> None:
        self._write(f"<?{target} {data}?>")

    def comment(self, comment: str) -> None:
        self._write("<!-- ")
        self._write(comment.replace("-->", "- ->"))
        self._write(" -->")
