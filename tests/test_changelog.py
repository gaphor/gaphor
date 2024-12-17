from pathlib import Path
from xml.etree import ElementTree as etree

import pytest
from markdown_it import MarkdownIt

# The release description field in a release supports a small subset of HTML:
# * p, ol, ul, li, em, code (no nested lists).
# * Only <p> and <li> may contain a `xml:lang` attribute.
#
# https://www.freedesktop.org/software/appstream/docs/chap-Metadata.html#tag-description


def versions(changelog_md: str):
    md = MarkdownIt("default", {"breaks": False, "html": True})
    html = md.render(changelog_md)
    changelog = etree.fromstring(f"<root>{html}</root>")

    version = "INVALID"
    news: dict[str, etree.Element] = {}

    for node in changelog:
        if node.tag == "h2" and node.text:
            version = node.text
            news[version] = etree.Element("description")
        else:
            news[version].append(node)

    return news


@pytest.mark.parametrize(
    "version,description",
    list(versions(Path("CHANGELOG.md").read_text("utf-8")).items()),
)
def test_changelog_is_appdata_compliant(version, description):
    whitelist_top = ["p", "ol", "ul", "em", "code"]
    whitelist_nested = ["li", "em", "code"]

    def _test_nested(elem):
        for e in elem:
            assert e.tag in whitelist_nested
            _test_nested(e)

    for e in description:
        assert e.tag in whitelist_top
        _test_nested(e)
