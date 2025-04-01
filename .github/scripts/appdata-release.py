# ruff: noqa T201
#
# Find the latest (top most) version from the appdata.

from xml.etree import ElementTree as etree

tree = etree.parse("data/org.gaphor.Gaphor.appdata.xml")

if (release := tree.find("./releases/release")) is not None:
    print(release.attrib["version"])
