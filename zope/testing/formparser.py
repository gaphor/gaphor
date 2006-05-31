"""HTML parser that extracts form information.

This is intended to support functional tests that need to extract
information from HTML forms returned by the publisher.

See *formparser.txt* for documentation.

"""
__docformat__ = "reStructuredText"

import HTMLParser
import urlparse


def parse(data, base=None):
    """Return a form collection parsed from `data`.

    `base` should be the URL from which `data` was retrieved.

    """
    parser = FormParser(data, base)
    return parser.parse()


class FormParser(object):

    def __init__(self, data, base=None):
        self.data = data
        self.base = base
        self._parser = HTMLParser.HTMLParser()
        self._parser.handle_data = self._handle_data
        self._parser.handle_endtag = self._handle_endtag
        self._parser.handle_starttag = self._handle_starttag
        self._parser.handle_startendtag = self._handle_starttag
        self._buffer = []
        self.current = None
        self.forms = FormCollection()

    def parse(self):
        """Parse the document, returning the collection of forms."""
        self._parser.feed(self.data)
        self._parser.close()
        return self.forms

    # HTMLParser handlers

    def _handle_data(self, data):
        self._buffer.append(data)

    def _handle_endtag(self, tag):
        if tag == "textarea":
            self.textarea.value = "".join(self._buffer)
            self.textarea = None
        elif tag == "select":
            self.select = None
        elif tag == "option":
            option = self.select.options[-1]
            label = "".join(self._buffer)
            if not option.label:
                option.label = label
            if not option.value:
                option.value = label
            if option.selected:
                if self.select.multiple:
                    self.select.value.append(option.value)
                else:
                    self.select.value = option.value

    def _handle_starttag(self, tag, attrs):
        del self._buffer[:]
        d = {}
        for name, value in attrs:
            d[name] = value
        name = d.get("name")
        id = d.get("id") or d.get("xml:id")
        if tag == "form":
            method = kwattr(d, "method", "get")
            action = d.get("action", "").strip() or None
            if self.base and action:
                action = urlparse.urljoin(self.base, action)
            enctype = kwattr(d, "enctype", "application/x-www-form-urlencoded")
            self.current = Form(name, id, method, action, enctype)
            self.forms.append(self.current)
        elif tag == "input":
            type = kwattr(d, "type", "text")
            checked = "checked" in d
            disabled = "disabled" in d
            readonly = "readonly" in d
            src = d.get("src", "").strip() or None
            if self.base and src:
                src = urlparse.urljoin(self.base, src)
            value = d.get("value")
            size = intattr(d, "size")
            maxlength = intattr(d, "maxlength")
            self.current[name] = Input(name, id, type, value,
                                       checked, disabled, readonly,
                                       src, size, maxlength)
        elif tag == "button":
            pass
        elif tag == "textarea":
            disabled = "disabled" in d
            readonly = "readonly" in d
            self.textarea = Input(name, id, "textarea", None,
                                  None, disabled, readonly,
                                  None, None, None)
            self.textarea.rows = intattr(d, "rows")
            self.textarea.cols = intattr(d, "cols")
            self.current[name] = self.textarea
            # The value will be set when the </textarea> is seen.
        elif tag == "base":
            href = d.get("href", "").strip()
            if href and self.base:
                href = urlparse.urljoin(self.base, href)
            self.base = href
        elif tag == "select":
            disabled = "disabled" in d
            multiple = "multiple" in d
            size = intattr(d, "size")
            self.select = Select(name, id, disabled, multiple, size)
            self.current[name] = self.select
        elif tag == "option":
            disabled = "disabled" in d
            selected = "selected" in d
            value = d.get("value")
            label = d.get("label")
            option = Option(id, value, selected, label, disabled)
            self.select.options.append(option)


def kwattr(d, name, default=None):
    """Return attribute, converted to lowercase."""
    v = d.get(name, default)
    if v != default and v is not None:
        v = v.strip().lower()
        v = v or default
    return v


def intattr(d, name):
    """Return attribute as an integer, or None."""
    if name in d:
        v = d[name].strip()
        return int(v)
    else:
        return None


class FormCollection(list):
    """Collection of all forms from a page."""

    def __getattr__(self, name):
        for form in self:
            if form.name == name:
                return form
        raise AttributeError, name


class Form(dict):
    """A specific form within a page."""

    def __init__(self, name, id, method, action, enctype):
        super(Form, self).__init__()
        self.name = name
        self.id = id
        self.method = method
        self.action = action
        self.enctype = enctype


class Input(object):
    """Input element."""

    rows = None
    cols = None

    def __init__(self, name, id, type, value, checked, disabled, readonly,
                 src, size, maxlength):
        super(Input, self).__init__()
        self.name = name
        self.id = id
        self.type = type
        self.value = value
        self.checked = checked
        self.disabled = disabled
        self.readonly = readonly
        self.src = src
        self.size = size
        self.maxlength = maxlength


class Select(Input):
    """Select element."""

    def __init__(self, name, id, disabled, multiple, size):
        super(Select, self).__init__(name, id, "select", None, None,
                                     disabled, None, None, size, None)
        self.options = []
        self.multiple = multiple
        if multiple:
            self.value = []


class Option(object):
    """Individual value representation for a select element."""

    def __init__(self, id, value, selected, label, disabled):
        super(Option, self).__init__()
        self.id = id
        self.value = value
        self.selected = selected
        self.label = label
        self.disabled = disabled
