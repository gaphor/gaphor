from gaphas.canvas import instant_cairo_context

from gaphor import UML
from gaphor.core.modeling import DrawContext
from gaphor.core.modeling.diagram import FALLBACK_STYLE
from gaphor.UML.actions.flow import ControlFlowItem


def test_create_flow(diagram, element_factory):
    flow = element_factory.create(UML.ControlFlow)
    item = diagram.create(ControlFlowItem, subject=flow)

    assert item.subject is flow


def test_name(diagram, element_factory):
    """Test updating of flow name text."""
    flow = diagram.create(
        ControlFlowItem, subject=element_factory.create(UML.ControlFlow)
    )
    name = flow.shape_tail.children[1]

    flow.subject.name = "Blah"

    assert "Blah" == name.text()

    flow.subject = None

    assert "" == name.text()


def test_guard_text_update(diagram, element_factory):
    flow = diagram.create(
        ControlFlowItem, subject=element_factory.create(UML.ControlFlow)
    )
    guard = flow.shape_middle

    assert "" == guard.text()

    flow.subject.guard = "GuardMe"
    assert "[GuardMe]" == guard.text()

    flow.subject = None
    assert "" == guard.text()


def test_draw(diagram, element_factory):
    flow = diagram.create(
        ControlFlowItem, subject=element_factory.create(UML.ControlFlow)
    )
    context = DrawContext(
        cairo=instant_cairo_context(),
        style=FALLBACK_STYLE,
        hovered=True,
        focused=True,
        selected=True,
        dropzone=False,
    )
    diagram.update_now((flow,))
    flow.draw(context)
