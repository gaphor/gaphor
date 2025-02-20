from gaphor.core.changeset.compare import set_value_change_property_value
from gaphor.core.modeling import ElementChange, ValueChange
from gaphor.ui.modelmerge.editor import ModelMerge


def test_build_list_store(event_manager, element_factory, modeling_language):
    model_merge = ModelMerge(event_manager, element_factory, modeling_language)

    change: ElementChange = element_factory.create(ElementChange)
    change.op = "add"
    change.element_id = "1234"
    change.element_name = "Diagram"
    vchange: ValueChange = element_factory.create(ValueChange)
    vchange.op = "update"
    vchange.element_id = "1234"
    vchange.property_name = "name"
    set_value_change_property_value(vchange, "my diagram")

    model_merge.refresh_model()

    assert model_merge.model
    assert not model_merge.model[0].children
