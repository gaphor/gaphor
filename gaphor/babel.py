import io

import defusedxml.ElementTree as etree

from gaphor.i18n import gettext


def extract_gaphor(fileobj, keywords, comment_tags, options):
    """Extract text from Gaphor models.

    Args:
        fileobj (obj): the file-like object the messages should be extracted from.
        keywords (list): a list of keywords (i.e. function names) that should
              be recognized as translation functions.
        comment_tags (list): a list of translator tags to search for and
                  include in the results.
        options (dict, optional) : a dictionary of additional options.
    Returns:
        iterator: an iterator over ``(lineno, funcname, message, comments)``
             tuples.

    See also:

    * babel.messages.extract.extract()
    * http://babel.pocoo.org/en/latest/messages.html#writing-extraction-methods
    * https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html
    """
    lineno = None
    funcname = "gettext"
    comments: list[str] = []

    tree = etree.parse(fileobj)

    for node in translatable_nodes(tree):
        yield (lineno, funcname, node.text, comments)


def translate_model(fileobj):
    tree = etree.parse(fileobj)

    for node in translatable_nodes(tree):
        node.text = gettext(node.text) if node.text else ""

    return io.StringIO(etree.tostring(tree.getroot(), encoding="unicode", method="xml"))


def translatable_nodes(tree):
    NS = {"g": "http://gaphor.sourceforge.net/model"}

    for tag in ("name", "body", "typeValue"):
        yield from tree.findall(f".//g:{tag}/g:val", NS)
