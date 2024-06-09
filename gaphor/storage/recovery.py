import ast
import hashlib
import logging
from collections.abc import Iterator
from io import IOBase
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

log = logging.getLogger(__name__)


def sessions_dir() -> Path:
    d = settings.get_cache_dir() / "sessions"
    d.mkdir(exist_ok=True)
    return d


def all_sessions() -> Iterator[tuple[str, Path | None, Path | None]]:
    """Get all open active/inactive sessions.

    Returns a list of tuples: session id, filename path, template path.
    """
    for session_file in sessions_dir().glob("*.recovery"):
        with session_file.open(encoding="utf-8") as f:
            preamble_line = f.readline()
        if preamble_line:
            try:
                preamble = ast.literal_eval(preamble_line)
                path = Path(preamble.get("path"))
                is_template = preamble.get("template", False)
                if path.exists() and path.is_file():
                    yield (
                        (session_file.stem, None, Path(path))
                        if is_template
                        else (session_file.stem, Path(path), None)
                    )
                else:
                    log.info("Session file does not reference an existing model file.")
                    _move_aside(session_file)
            except (SyntaxError, TypeError, AttributeError):
                log.info("File has an invalid header: '%s'.", preamble_line)
                _move_aside(session_file)


class Recovery(Service):
    def __init__(self, event_manager, element_factory, modeling_language):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.modeling_language = modeling_language
        self.session_id: str = "_"
        self.recorder = Recorder()
        self.event_log: EventLog | None = None

        event_manager.subscribe(self.on_transaction_commit)
        event_manager.subscribe(self.on_transaction_rollback)
        event_manager.subscribe(self.on_model_loaded)
        event_manager.subscribe(self.on_model_ready)
        event_manager.subscribe(self.on_model_saved)
        event_manager.subscribe(self.on_session_shutdown)

        self.recorder.subscribe(event_manager)

    def shutdown(self):
        if self.event_log:
            self.event_log.close()

        self.event_manager.unsubscribe(self.on_transaction_commit)
        self.event_manager.unsubscribe(self.on_transaction_rollback)
        self.event_manager.unsubscribe(self.on_model_loaded)
        self.event_manager.unsubscribe(self.on_model_ready)
        self.event_manager.unsubscribe(self.on_model_saved)
        self.event_manager.unsubscribe(self.on_session_shutdown)

        self.recorder.unsubscribe(self.event_manager)

    @event_handler(TransactionCommit)
    def on_transaction_commit(self, event: TransactionCommit):
        if (
            self.event_log
            and self.recorder.events
            and event.context not in ("rollback", "recover")
        ):
            self.event_log.write(self.recorder.events)
        self.recorder.truncate()

    @event_handler(TransactionRollback)
    def on_transaction_rollback(self, _event):
        self.recorder.truncate()

    @event_handler(SessionCreated)
    def on_model_loaded(self, event: SessionCreated):
        self.session_id = event.session.session_id
        if event.filename or event.template:
            self.event_log = EventLog(self.session_id, event.filename, event.template)
        self.recorder.truncate()

    @event_handler(ModelReady)
    def on_model_ready(self, _event):
        if not self.event_log:
            return

        events = []
        try:
            with Transaction(self.event_manager, context="recover"):
                for events in self.event_log.read():
                    replay_events(events, self.element_factory, self.modeling_language)
        except Exception:
            log.error(
                "Could not recover model changes from %s. Changes have been rolled back.",
                self.event_log.log_file,
                exc_info=True,
            )
            log.warning("Replaying events failed.")
            self.event_log.move_aside()

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
        if self.event_log:
            self.event_log.clear()

        if event.filename:
            self.event_log = EventLog(self.session_id, event.filename)
            self.event_log.clear()
        else:
            self.event_log = None

        self.recorder.truncate()

    @event_handler(SessionShutdown)
    def on_session_shutdown(self, _event: SessionShutdown):
        if self.event_log:
            self.event_log.clear()
        self.recorder.truncate()


class EventLog:
    def __init__(
        self, session_id: str, filename: Path | None, template: Path | None = None
    ):
        self._filename = filename
        self._template = template
        self._log_name = (sessions_dir() / session_id).with_suffix(".recovery")

        # The file that we use to save the events to:
        self._file: IOBase | None = None

    @property
    def log_file(self):
        return self._log_name

    def clear(self):
        self.close()
        self._log_name.unlink(missing_ok=True)

    def write(self, event):
        if not (self._filename or self._template):
            return

        f = self._file
        if not f or f.closed:
            f = self._file = self._log_name.open(mode="a", encoding="utf-8")

        if f.tell() == 0:
            if self._template:
                filename = self._template.absolute()
                is_template = True
            else:
                assert self._filename
                filename = self._filename.absolute()
                is_template = False

            f.write(
                repr(
                    {
                        "path": str(filename.absolute()),
                        "sha256": sha256sum(filename),
                        "template": is_template,
                    }
                )
            )
            f.write("\n")

        f.write(repr(event))
        f.write("\n")
        f.flush()

    def read(self):
        if not (self._filename or self._template):
            return

        self.close()
        try:
            with self._log_name.open(mode="r", encoding="utf-8") as f:
                preamble_line = f.readline()
                preamble = ast.literal_eval(preamble_line)
                if not isinstance(preamble, dict):
                    raise ChecksumFailed()

                filename = (
                    self._template if preamble.get("template") else self._filename
                )
                if not filename or sha256sum(filename) != preamble.get("sha256"):
                    raise ChecksumFailed()

                for line in f:
                    events = ast.literal_eval(line.rstrip("\r\n"))
                    yield events

        except FileNotFoundError:
            # Log does not exist, no problem
            pass
        except ChecksumFailed:
            # Move file after it's closed.
            log.info("Recovery file hash does not match.")
            self.move_aside()

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def move_aside(self):
        self.close()
        _move_aside(self._log_name)


class ChecksumFailed(Exception):
    pass


def _move_aside(path: Path):
    backup = path.with_suffix(".recovery.bak")
    path.rename(backup)
    log.info("Session recovery file is renamed to %s.", backup)


def sha256sum(filename: Path):
    with open(filename, "rb", buffering=0) as f:
        return hashlib.file_digest(f, "sha256").hexdigest()  # type: ignore[arg-type]


class Recorder:
    def __init__(self):
        self.events = []

    def subscribe(self, event_manager):
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

    def unsubscribe(self, event_manager):
        event_manager.unsubscribe(self.on_create_element_event)
        event_manager.unsubscribe(self.on_delete_element_event)
        event_manager.unsubscribe(self.on_attribute_change_event)
        event_manager.unsubscribe(self.on_association_set_event)
        event_manager.unsubscribe(self.on_association_delete_event)
        event_manager.unsubscribe(self.on_matrix_updated)
        event_manager.unsubscribe(self.on_item_connected)
        event_manager.unsubscribe(self.on_item_disconnected)
        event_manager.unsubscribe(self.on_item_reconnected)
        event_manager.unsubscribe(self.on_handle_position_event)
        event_manager.unsubscribe(self.on_split_line_segment_event)
        event_manager.unsubscribe(self.on_merge_line_segment_event)

    def truncate(self):
        del self.events[:]

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

    # We handle all RevertibleEvent subtypes separately:
    #
    # - gaphor.core.modeling.presentation.MatrixUpdated
    # - gaphor.diagram.presentation.HandlePositionEvent
    # - gaphor.diagram.connectors.ItemConnected
    # - gaphor.diagram.connectors.ItemDisconnected
    # - gaphor.diagram.connectors.ItemReconnected
    # - gaphor.diagram.tools.segment.LineSplitSegmentEvent
    # - gaphor.diagram.tools.segment.LineMergeSegmentEvent
    #
    # We can ignore gaphor.diagram.connectors.ItemTemporaryDisconnected,
    # since it has no (direct) impact on the model state.

    @event_handler(MatrixUpdated)
    def on_matrix_updated(self, event: MatrixUpdated):
        self.events.append(("mu", event.element.id, event.new_value))

    @event_handler(HandlePositionEvent)
    def on_handle_position_event(self, event: HandlePositionEvent):
        self.events.append(
            ("hp", event.element.id, event.handle_index, event.new_value)
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
    """Replay events previously recorded by EventLog."""
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
