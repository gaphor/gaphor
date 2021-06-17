from gaphor.diagram.general import Line
from gaphor.diagram.propertypages import LineStylePage, NotePropertyPage
from gaphor.diagram.tests.fixtures import find


def test_line_style_page_rectilinear(diagram):
    item = diagram.create(Line)
    property_page = LineStylePage(item)
    widget = property_page.construct()
    line_rectangular = find(widget, "line-rectilinear")

    line_rectangular.set_active(True)

    assert item.orthogonal


def test_line_style_page_orientation(diagram):
    item = diagram.create(Line)
    property_page = LineStylePage(item)
    widget = property_page.construct()
    flip_orientation = find(widget, "flip-orientation")
    flip_orientation.set_active(True)

    assert item.horizontal


def test_note_page(diagram):
    item = diagram.create(Line)
    property_page = NotePropertyPage(item)
    widget = property_page.construct()
    note = find(widget, "note")
    note.get_buffer().set_text("A new note")

    assert item.note == "A new note"
