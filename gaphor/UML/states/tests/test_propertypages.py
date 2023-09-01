from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.states.propertypages import (
    RegionPropertyPage,
    StatePropertyPage,
    TransitionPropertyPage,
)
from gaphor.UML.states.state import StateItem


def test_state_property_page_entry(element_factory):
    # Create some behavior elements
    opt1 = element_factory.create(UML.Activity)
    opt1.name = "option 1"

    opt2 = element_factory.create(UML.Interaction)
    opt2.name = "option 2"

    # Create subject property page
    subject = element_factory.create(UML.State)
    property_page = StatePropertyPage(subject)

    widget = property_page.construct()
    do_activity = find(widget, "entry")

    do_activity.set_selected(0)
    assert not subject.entry

    do_activity.set_selected(1)
    assert (
        subject.entry
        and isinstance(subject.entry, UML.Activity)
        and subject.entry.name == "option 1"
    )

    do_activity.set_selected(2)
    assert (
        subject.entry
        and isinstance(subject.entry, UML.Interaction)
        and subject.entry.name == "option 2"
    )

    do_activity.set_selected(0)
    assert not subject.entry


def test_state_property_page_exit(element_factory):
    # Create some behavior elements
    opt1 = element_factory.create(UML.Activity)
    opt1.name = "option 1"

    opt2 = element_factory.create(UML.Interaction)
    opt2.name = "option 2"

    # Create subject property page
    subject = element_factory.create(UML.State)
    property_page = StatePropertyPage(subject)

    widget = property_page.construct()
    do_activity = find(widget, "exit")

    do_activity.set_selected(0)
    assert not subject.exit

    do_activity.set_selected(1)
    assert (
        subject.exit
        and isinstance(subject.exit, UML.Activity)
        and subject.exit.name == "option 1"
    )

    do_activity.set_selected(2)
    assert (
        subject.exit
        and isinstance(subject.exit, UML.Interaction)
        and subject.exit.name == "option 2"
    )

    do_activity.set_selected(0)
    assert not subject.exit


def test_state_property_page_do_activity(element_factory):
    # Create some behavior elements
    opt1 = element_factory.create(UML.Activity)
    opt1.name = "option 1"

    opt2 = element_factory.create(UML.Interaction)
    opt2.name = "option 2"

    # Create subject property page
    subject = element_factory.create(UML.State)
    property_page = StatePropertyPage(subject)

    widget = property_page.construct()
    do_activity = find(widget, "do-activity")

    do_activity.set_selected(0)
    assert not subject.doActivity

    do_activity.set_selected(1)
    assert (
        subject.doActivity
        and isinstance(subject.doActivity, UML.Activity)
        and subject.doActivity.name == "option 1"
    )

    do_activity.set_selected(2)
    assert (
        subject.doActivity
        and isinstance(subject.doActivity, UML.Interaction)
        and subject.doActivity.name == "option 2"
    )

    do_activity.set_selected(0)
    assert not subject.doActivity


def test_transition_property_page(element_factory):
    subject = element_factory.create(UML.Transition)
    property_page = TransitionPropertyPage(subject)

    widget = property_page.construct()
    guard = find(widget, "guard")
    guard.set_text("test")

    assert subject.guard.specification == "test"


def test_region_property_page(create):
    item = create(StateItem, UML.State)
    property_page = RegionPropertyPage(item)

    widget = property_page.construct()
    num_regions = find(widget, "num-regions")
    num_regions.set_value(4)

    assert len(item.subject.region) == 4
