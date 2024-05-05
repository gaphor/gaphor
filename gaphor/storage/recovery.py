import ast
from pathlib import Path

from gaphor import settings
from gaphor.abc import Service
from gaphor.core import event_handler
from gaphor.core.modeling import (
    AssociationAdded,
    AssociationDeleted,
    AssociationSet,
    AttributeUpdated,
    DerivedUpdated,
    ElementCreated,
    ElementDeleted,
    ModelReady,
    RedefinedAdded,
    RedefinedDeleted,
    RedefinedSet,
)
from gaphor.core.modeling.presentation import MatrixUpdated
from gaphor.diagram.connectors import (
    ItemConnected,
    ItemDisconnected,
    ItemReconnected,
    ItemTemporaryDisconnected,
)
from gaphor.diagram.presentation import HandlePositionEvent
from gaphor.diagram.segment import LineMergeSegmentEvent, LineSplitSegmentEvent
from gaphor.event import (
    ModelSaved,
    Notification,
    SessionCreated,
    SessionShutdown,
)
from gaphor.i18n import gettext
from gaphor.transaction import Transaction, TransactionCommit, TransactionRollback


def recovery_filename(filename: Path) -> Path:
    return (settings.get_cache_dir() / settings.file_hash(filename)).with_suffix(
        ".recovery"
    )


class Recovery(Service):
    def __init__(self, event_manager, element_factory, modeling_language):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.modeling_language = modeling_language
        # TODO: How to record new, unsaved models?
        self.filename: Path | None = None
        self.events = []

        event_manager.subscribe(self.on_transaction_commit)
        event_manager.subscribe(self.on_transaction_rollback)
        event_manager.subscribe(self.on_model_loaded)
        event_manager.subscribe(self.on_model_ready)
        event_manager.subscribe(self.on_model_saved)
        event_manager.subscribe(self.on_session_shutdown)

        event_manager.subscribe(self.on_create_element_event)
        event_manager.subscribe(self.on_delete_element_event)
        event_manager.subscribe(self.on_attribute_change_event)
        event_manager.subscribe(self.on_association_set_event)
        event_manager.subscribe(self.on_association_delete_event)
        event_manager.subscribe(self.on_matrix_updated)
        event_manager.subscribe(self.on_item_connected)
        event_manager.subscribe(self.on_item_disconnected)
        event_manager.subscribe(self.on_item_reconnected)
        event_manager.subscribe(self.on_handle_position_event)
        event_manager.subscribe(self.on_split_line_segment_event)
        event_manager.subscribe(self.on_merge_line_segment_event)

    def shutdown(self):
        self.event_manager.unsubscribe(self.on_transaction_commit)
        self.event_manager.unsubscribe(self.on_transaction_rollback)
        self.event_manager.unsubscribe(self.on_model_loaded)
        self.event_manager.unsubscribe(self.on_model_ready)
        self.event_manager.unsubscribe(self.on_model_saved)
        self.event_manager.unsubscribe(self.on_session_shutdown)

        self.event_manager.unsubscribe(self.on_create_element_event)
        self.event_manager.unsubscribe(self.on_delete_element_event)
        self.event_manager.unsubscribe(self.on_attribute_change_event)
        self.event_manager.unsubscribe(self.on_association_set_event)
        self.event_manager.unsubscribe(self.on_association_delete_event)
        self.event_manager.unsubscribe(self.on_matrix_updated)
        self.event_manager.unsubscribe(self.on_item_connected)
        self.event_manager.unsubscribe(self.on_item_disconnected)
        self.event_manager.unsubscribe(self.on_item_reconnected)
        self.event_manager.unsubscribe(self.on_handle_position_event)
        self.event_manager.unsubscribe(self.on_split_line_segment_event)
        self.event_manager.unsubscribe(self.on_merge_line_segment_event)

    def truncate(self):
        del self.events[:]

    @event_handler(TransactionCommit)
    def on_transaction_commit(self, event: TransactionCommit):
        if (
            self.filename
            and self.events
            and event.context not in ("rollback", "recover")
        ):
            with self.filename.open("a", encoding="utf-8") as f:
                f.write(repr(self.events))
                f.write("\n")
        self.truncate()

    @event_handler(TransactionRollback)
    def on_transaction_rollback(self, _event):
        self.truncate()

    @event_handler(SessionCreated)
    def on_model_loaded(self, event: SessionCreated):
        self.filename = recovery_filename(event.filename) if event.filename else None
        self.truncate()

    @event_handler(ModelReady)
    def on_model_ready(self, _event):
        if not self.filename or not self.filename.exists():
            return

        events = []
        with Transaction(self.event_manager, context="recover"):
            for line in self.filename.open(encoding="utf-8"):
                events = ast.literal_eval(line.rstrip("\r\n"))
                replay_events(events, self.element_factory, self.modeling_language)

            # Ensure events are not recorded again
            self.truncate()

        if events:
            self.event_manager.handle(
                Notification(
                    gettext(
                        "This model contains unsaved changes. The changes have been restored."
                    )
                )
            )

    @event_handler(ModelSaved)
    def on_model_saved(self, event: ModelSaved):
        if self.filename:
            self.filename.unlink(missing_ok=True)

        self.filename = recovery_filename(event.filename) if event.filename else None

        # Delete again: new model name may be different from original one
        if self.filename:
            self.filename.unlink(missing_ok=True)
        self.truncate()

    @event_handler(SessionShutdown)
    def on_session_shutdown(self, event: SessionShutdown):
        if self.filename:
            self.filename.unlink(missing_ok=True)
        self.truncate()

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
        if isinstance(event, (DerivedUpdated, RedefinedAdded, RedefinedSet)):
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
        if isinstance(event, (DerivedUpdated, RedefinedDeleted)):
            return
        self.events.append(
            (
                "d",
                event.element.id,
                event.property.name,
                event.old_value and event.old_value.id,
            )
        )

    # We should handle all RevertibleEvent subtypes separately:
    # gaphor.core.modeling.presentation.MatrixUpdated
    # gaphor.diagram.presentation.HandlePositionEvent
    # gaphor.diagram.connectors.ItemConnected
    # gaphor.diagram.connectors.ItemDisconnected
    # ignore: gaphor.diagram.connectors.ItemTemporaryDisconnected
    # gaphor.diagram.connectors.ItemReconnected
    # gaphor.diagram.tools.segment.LineSplitSegmentEvent
    # gaphor.diagram.tools.segment.LineMergeSegmentEvent

    @event_handler(MatrixUpdated)
    def on_matrix_updated(self, event: MatrixUpdated):
        self.events.append(("mu", event.element.id, tuple(event.element.matrix)))

    @event_handler(HandlePositionEvent)
    def on_handle_position_event(self, event: HandlePositionEvent):
        pos = event.element.handles()[event.handle_index].pos
        self.events.append(
            ("hp", event.element.id, event.handle_index, (float(pos.x), float(pos.y)))
        )

    @event_handler(ItemConnected)
    def on_item_connected(self, event: ItemConnected):
        self.events.append(
            (
                "ic",
                event.element.id,
                event.handle_index,
                event.connected_id,
                event.port_index,
            )
        )

    @event_handler(ItemDisconnected)
    def on_item_disconnected(self, event: ItemDisconnected):
        self.events.append(
            (
                "id",
                event.element.id,
                event.handle_index,
                event.connected_id,
                event.port_index,
            )
        )

    @event_handler(ItemReconnected)
    def on_item_reconnected(self, event: ItemReconnected):
        self.events.append(
            (
                "ir",
                event.element.id,
                event.handle_index,
                event.connected_id,
                event.port_index,
            )
        )

    @event_handler(LineSplitSegmentEvent)
    def on_split_line_segment_event(self, event: LineSplitSegmentEvent):
        self.events.append(
            (
                "ls",
                event.element.id,
                event.segment,
                event.count,
            )
        )

    @event_handler(LineMergeSegmentEvent)
    def on_merge_line_segment_event(self, event: LineMergeSegmentEvent):
        self.events.append(
            (
                "lm",
                event.element.id,
                event.segment,
                event.count,
            )
        )


def replay_events(events, element_factory, modeling_language):
    for event in events:
        match event:
            case ("c", type, element_id, None):
                element_factory.create_as(
                    modeling_language.lookup_element(type), element_id
                )
            case ("c", type, element_id, diagram_id):
                diagram = element_factory.lookup(diagram_id)
                diagram.create_as(modeling_language.lookup_element(type), element_id)
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
            case ("mu", element_id, matrix):
                element = element_factory.lookup(element_id)
                element.matrix.set(*matrix)
            case ("hp", element_id, handle_index, pos):
                element = element_factory.lookup(element_id)
                element.handles()[handle_index].pos = pos
            case ("ic", element_id, handle_index, connected_id, port_index):
                element = element_factory.lookup(element_id)
                connected = element_factory.lookup(connected_id)
                ItemDisconnected(
                    element,
                    element.handles()[handle_index],
                    connected,
                    connected.ports()[port_index],
                ).revert(element)
            case ("id", element_id, handle_index, connected_id, port_index):
                element = element_factory.lookup(element_id)
                connected = element_factory.lookup(connected_id)
                ItemConnected(
                    element,
                    element.handles()[handle_index],
                    connected,
                    connected.ports()[port_index],
                ).revert(element)
            case ("ir", element_id, handle_index, connected_id, port_index):
                element = element_factory.lookup(element_id)
                connected = element_factory.lookup(connected_id)
                ItemTemporaryDisconnected(
                    element,
                    element.handles()[handle_index],
                    connected,
                    connected.ports()[port_index],
                ).revert(element)
            case ("ls", element_id, segment, count):
                element = element_factory.lookup(element_id)
                LineMergeSegmentEvent(element, segment, count).revert(element)
            case ("lm", element_id, segment, count):
                element = element_factory.lookup(element_id)
                LineSplitSegmentEvent(element, segment, count).revert(element)
            case _:
                assert NotImplementedError(f"Event {event} not implemented")
