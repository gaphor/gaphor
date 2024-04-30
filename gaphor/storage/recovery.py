from pathlib import Path

from gaphor import settings
from gaphor.abc import Service
from gaphor.core import event_handler
from gaphor.core.modeling.event import (
    AssociationAdded,
    AssociationDeleted,
    AssociationSet,
    AttributeUpdated,
    DerivedUpdated,
    ElementCreated,
    ElementDeleted,
    RevertibleEvent,
)
from gaphor.event import ModelSaved, SessionCreated


def recovery_filename(filename: str) -> Path:
    return (settings.get_cache_dir() / settings.file_hash(filename)).with_suffix(
        ".recovery"
    )


class Recovery(Service):
    def __init__(self, event_manager, element_factory):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.filename: Path = recovery_filename("")
        self.events = []

        event_manager.subscribe(self.on_model_loaded)
        event_manager.subscribe(self.on_model_saved)

        event_manager.subscribe(self.on_reversible_event)
        event_manager.subscribe(self.on_create_element_event)
        event_manager.subscribe(self.on_delete_element_event)
        event_manager.subscribe(self.on_attribute_change_event)
        event_manager.subscribe(self.on_association_set_event)
        event_manager.subscribe(self.on_association_delete_event)

    def shutdown(self):
        self.event_manager.unsubscribe(self.on_model_loaded)
        self.event_manager.unsubscribe(self.on_model_saved)

        self.event_manager.unsubscribe(self.on_reversible_event)
        self.event_manager.unsubscribe(self.on_create_element_event)
        self.event_manager.unsubscribe(self.on_delete_element_event)
        self.event_manager.unsubscribe(self.on_attribute_change_event)
        self.event_manager.unsubscribe(self.on_association_set_event)
        self.event_manager.unsubscribe(self.on_association_delete_event)

    def replay(self, element_factory, modeling_language):
        for event in list(self.events):
            match event:
                case ("c", type, element_id, None):
                    element_factory.create_as(
                        modeling_language.lookup_element(type), element_id
                    )
                case ("c", type, element_id, diagram_id):
                    diagram = element_factory.lookup(diagram_id)
                    diagram.create_as(
                        modeling_language.lookup_element(type), element_id
                    )
                case ("u", element_id, _diagram_id):
                    element_factory.lookup(element_id).unlink()
                case ("a", element_id, prop, value):
                    element = element_factory.lookup(element_id)
                    setattr(element, prop, value)
                case ("s", element_id, prop, other_element_id):
                    element = element_factory.lookup(element_id)
                    other_element = element_factory.lookup(other_element_id)
                    setattr(element, prop, other_element)
                case ("d", element_id, prop, other_element_id):
                    element = element_factory.lookup(element_id)
                    other_element = element_factory.lookup(other_element_id)
                    del getattr(element, prop)[other_element]
                case _:
                    assert NotImplementedError(f"Event {event} not implemented")

    def truncate(self):
        del self.events[:]

    @event_handler(SessionCreated)
    def on_model_loaded(self, event):
        self.filename = recovery_filename(event.filename or "")

    @event_handler(ModelSaved)
    def on_model_saved(self, event):
        self.filename = recovery_filename(event.filename or "")
        self.truncate()

    @event_handler(RevertibleEvent)
    def on_reversible_event(self, event: RevertibleEvent):
        # We should handle all RevertibleEvent subtypes separately:
        # gaphor.core.modeling.presentation.MatrixUpdated
        # gaphor.diagram.connectors.ItemConnected
        # gaphor.diagram.connectors.ItemDisconnected
        # ignore: gaphor.diagram.connectors.ItemTemporaryDisconnected
        # gaphor.diagram.connectors.ItemReconnected
        # gaphor.diagram.presentation.HandlePositionEvent
        # gaphor.diagram.tools.segment.LineSplitSegmentEvent
        # gaphor.diagram.tools.segment.LineMergeSegmentEvent
        ...

    @event_handler(ElementCreated)
    def on_create_element_event(self, event: ElementCreated):
        self.events.append(
            (
                "c",
                type(event.element).__name__,
                event.element.id,
                event.diagram and event.diagram.id,
            )
        )

    @event_handler(ElementDeleted)
    def on_delete_element_event(self, event: ElementDeleted):
        self.events.append(("u", event.element.id, event.diagram and event.diagram.id))

    @event_handler(AttributeUpdated)
    def on_attribute_change_event(self, event: AttributeUpdated):
        self.events.append(
            ("a", event.element.id, event.property.name, event.new_value)
        )

    @event_handler(AssociationAdded, AssociationSet)
    def on_association_set_event(self, event: AssociationSet | AssociationAdded):
        if isinstance(event, DerivedUpdated):
            return
        self.events.append(
            (
                "s",
                event.element.id,
                event.property.name,
                event.new_value and event.new_value.id,
            )
        )

    @event_handler(AssociationDeleted)
    def on_association_delete_event(self, event: AssociationDeleted):
        if isinstance(event, DerivedUpdated):
            return
        self.events.append(
            (
                "d",
                event.element.id,
                event.property.name,
                event.old_value and event.old_value.id,
            )
        )
