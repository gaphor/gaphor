from io import StringIO

import pytest
from defusedxml import EntitiesForbidden

from gaphor.storage.parser import parse


def test_parsing_v2_1_model_with_grouped_item(test_models):
    with open(test_models / "node-component-v2.1.gaphor", encoding="utf-8") as f:
        elements = parse(f)

    diagram = next(e for e in elements.values() if e.type == "Diagram")
    component_item = next(e for e in elements.values() if e.type == "ComponentItem")
    node_item = next(e for e in elements.values() if e.type == "NodeItem")

    assert component_item.references["parent"] == node_item.id
    assert component_item.references["diagram"] == diagram.id
    assert "parent" not in node_item.references
    assert node_item.references["diagram"] == diagram.id


def test_parsing_of_open_file(test_models):
    with (test_models / "test-model.gaphor").open(encoding="utf-8") as model:
        elements = parse(model)

    assert elements


def test_parsing_of_xml_entities():
    model = StringIO(
        """<?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE gaphor [
        <!ENTITY ent "okay" >]>
        <gaphor xmlns="http://gaphor.sourceforge.net/model" version="3.0" gaphor-version="2.9.2">
         <Package id="0">
          <name>
           <val>&ent;</val>
          </name>
         </Package>
        </gaphor>"""
    )

    with pytest.raises(EntitiesForbidden):
        parse(model)


def test_parsing_of_xml_external_entities_should_fail():
    model = StringIO(
        """<?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE gaphor [
        <!ENTITY xxe SYSTEM "https://gaphor.org/latest.txt" >]>
        <gaphor xmlns="http://gaphor.sourceforge.net/model" version="3.0" gaphor-version="2.9.2">
         <Package id="0">
          <name>
           <val>&xxe;</val>
          </name>
         </Package>
        </gaphor>"""
    )

    with pytest.raises(EntitiesForbidden):
        parse(model)
