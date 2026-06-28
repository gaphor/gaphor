import pytest
import pytest_asyncio

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.general import Box
from gaphor.ui.diagrampage import (
    DiagramPage,
    delete_selected_items,
)
from gaphor.UML import Comment
from gaphor.UML.diagramitems import ClassItem, PackageItem
from gaphor.UML.general.comment import CommentItem


@pytest_asyncio.fixture
async def page(diagram, event_manager, element_factory, modeling_language):
    page = DiagramPage(diagram, event_manager, element_factory, modeling_language)
    page.construct()
    assert page.diagram == diagram
    assert page.view.model == diagram
    yield page
    page.close()


def test_creation(page, element_factory):
    assert len(element_factory.lselect()) == 1
    assert len(element_factory.lselect(Diagram)) == 1


def test_placement(diagram, page, element_factory):
    box = diagram.create(Box)
    page.view.request_update([box])

    diagram.create(CommentItem, subject=element_factory.create(Comment))
    assert len(element_factory.lselect()) == 4


@pytest.mark.asyncio
async def test_delete_selected_items(create, diagram, view, event_manager):
    package_item = create(PackageItem, UML.Package)
    view.selection.select_items(package_item)
    await view.update()

    delete_selected_items(view, event_manager)

    assert not diagram.ownedPresentation


def test_delete_selected_owner(create, diagram, view, event_manager, sanitizer_service):
    class_item = create(ClassItem, UML.Class)
    diagram.element = class_item.subject
    view.selection.select_items(class_item)

    delete_selected_items(view, event_manager)

    assert not diagram.ownedPresentation
    assert diagram.element is None


@pytest.mark.asyncio
async def test_not_delete_selected_package_owner(
    create, diagram, view, event_manager, sanitizer_service
):
    package_item = create(PackageItem, UML.Package)
    package = package_item.subject
    diagram.element = package_item.subject
    view.selection.select_items(package_item)
    await view.update()

    delete_selected_items(view, event_manager)

    assert not diagram.ownedPresentation
    assert diagram.element is package
