from gaphor.core.modeling.element import generate_id


def upgrade_canvasitem(item, gaphor_version):
    upgrade_canvas_item_to_1_0_2(item)
    if version_lower_than(gaphor_version, (1, 1, 0)):
        upgrade_presentation_item_to_1_1_0(item)
        new_canvasitems = upgrade_message_item_to_1_1_0(item)
    else:
        new_canvasitems = []

    for i in [item] + new_canvasitems:
        upgrade_canvas_item_to_1_3_0(i)
        upgrade_implementation_item_to_interface_realization_item_to_2_3_0(i)
        upgrade_c4_diagram_item_name_to_2_4_3(i)

    return new_canvasitems


def version_lower_than(gaphor_version, version):
    """Only major and minor versions are checked.

    >>> version_lower_than("0.3.0", (0, 15, 0))
    True
    """
    parts = gaphor_version.split(".")

    return tuple(map(int, parts[:2])) < version[:2]


def upgrade_canvas_item_to_1_0_2(item):
    if item.type == "MetaclassItem":
        item.type = "ClassItem"
    elif item.type == "SubsystemItem":
        item.type = "ComponentItem"


def upgrade_presentation_item_to_1_1_0(item):
    if "show_stereotypes_attrs" in item.values:
        if item.type in (
            "ClassItem",
            "InterfaceItem",
            "ArtifactItem",
            "ComponentItem",
            "NodeItem",
        ):
            item.values["show_stereotypes"] = item.values["show_stereotypes_attrs"]
        del item.values["show_stereotypes_attrs"]

    if "drawing-style" in item.values:
        if item.type == "InterfaceItem":
            item.values["folded"] = "1" if item.values["drawing-style"] == "3" else "0"
        del item.values["drawing-style"]

    if "show-attributes" in item.values and item.type in ("ClassItem", "InterfaceItem"):
        item.values["show_attributes"] = item.values["show-attributes"]
        del item.values["show-attributes"]

    if "show-operations" in item.values and item.type in ("ClassItem", "InterfaceItem"):
        item.values["show_operations"] = item.values["show-operations"]
        del item.values["show-operations"]


def clone_canvasitem(item, subject_id):
    assert isinstance(item.references["subject"], str)
    new_item = type(item)(generate_id(), item.type)
    new_item.values = dict(item.values)
    new_item.references = dict(item.references)
    new_item.references["subject"] = subject_id
    return new_item


def upgrade_message_item_to_1_1_0(item):
    """Create new MessageItem's for each `message` and `inverted` message."""
    new_canvasitems = []
    if item.type == "MessageItem" and item.references.get("subject"):
        messages = item.references.get("message", [])
        inverted = item.references.get("inverted", [])
        if messages:
            del item.references["message"]
        if inverted:
            del item.references["inverted"]
        for m_id in messages:
            new_item = clone_canvasitem(item, m_id)
            new_canvasitems.append(new_item)
        for m_id in inverted:
            new_item = clone_canvasitem(item, m_id)
            new_canvasitems.append(new_item)
            (
                new_item.references["head-connection"],
                new_item.references["tail-connection"],
            ) = (
                new_item.references["tail-connection"],
                new_item.references["head-connection"],
            )
    return new_canvasitems


def upgrade_canvas_item_to_1_3_0(item):
    if item.type in ("InitialPseudostateItem", "HistoryPseudostateItem"):
        item.type = "PseudostateItem"


# since 2.3.0
def upgrade_implementation_item_to_interface_realization_item_to_2_3_0(item):
    if item.type == "ImplementationItem":
        item.type = "InterfaceRealizationItem"


def upgrade_c4_diagram_item_name_to_2_4_3(item):
    if item.type == "C4ContainerDatabaseItem":
        item.type = "C4DatabaseItem"
