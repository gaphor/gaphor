from gaphor.storage.parser import parse


def test_parsing_v2_1_model_with_grouped_item(test_models):
    elements = parse(test_models / "node-component-v2.1.gaphor")

    diagram = next(e for e in elements.values() if e.type == "Diagram")
    component_item = next(e for e in elements.values() if e.type == "ComponentItem")
    node_item = next(e for e in elements.values() if e.type == "NodeItem")

    assert component_item.references["parent"] == node_item.id
    assert component_item.references["diagram"] == diagram.id
    assert "parent" not in node_item.references
    assert node_item.references["diagram"] == diagram.id


def test_parsing_of_open_file(test_models):
    with (test_models / "test-model.gaphor").open() as model:
        elements = parse(model)

    assert elements
