from gi.repository import Gtk

from gaphor import UML
from gaphor.core import _, inject, transactional
from gaphor.diagram.propertypages import (
    PropertyPages,
    NamedItemPropertyPage,
    EditableTreeModel,
    create_hbox_label,
    create_tree_view,
    create_uml_combo,
)
from gaphor.diagram.interactions import MessageItem


class CommunicationMessageModel(EditableTreeModel):
    """GTK tree model for list of messages on communication diagram."""

    def __init__(self, item, cols=None, inverted=False):
        self.inverted = inverted
        super(CommunicationMessageModel, self).__init__(item, cols)

    def _get_rows(self):
        if self.inverted:
            for message in self._item._inverted_messages:
                yield [message.name, message]
        else:
            for message in self._item._messages:
                yield [message.name, message]

    def remove(self, iter):
        """Remove message from message item and destroy it."""

        message = self._get_object(iter)
        item = self._item
        super(CommunicationMessageModel, self).remove(iter)
        item.remove_message(message, self.inverted)

    def _create_object(self):
        item = self._item
        subject = item.subject
        message = UML.model.create_message(item.model, subject, self.inverted)
        item.add_message(message, self.inverted)
        return message

    def _set_object_value(self, row, col, value):
        message = row[-1]
        message.name = value
        row[0] = value
        self._item.set_message_text(message, value, self.inverted)

    def _swap_objects(self, o1, o2):
        return self._item.swap_messages(o1, o2, self.inverted)


@PropertyPages.register(MessageItem)
class MessagePropertyPage(NamedItemPropertyPage):
    """Property page for editing message items.

    When message is on communication diagram, then additional messages can
    be added. On sequence diagram sort of message can be changed.
    """

    element_factory = inject("element_factory")

    NAME_LABEL = _("Message")

    MESSAGE_SORT = (
        ("Call", "synchCall"),
        ("Asynchronous", "asynchCall"),
        ("Signal", "asynchSignal"),
        ("Create", "createMessage"),
        ("Delete", "deleteMessage"),
        ("Reply", "reply"),
    )

    def construct(self):
        page = super(MessagePropertyPage, self).construct()

        item = self.item
        subject = item.subject

        if not subject:
            return page

        if item.is_communication():
            self._messages = CommunicationMessageModel(item)
            tree_view = create_tree_view(self._messages, (_("Message"),))
            tree_view.set_headers_visible(False)
            frame = Gtk.Frame.new(label=_("Additional Messages"))
            frame.add(tree_view)
            page.pack_start(frame, True, True, 0)

            self._inverted_messages = CommunicationMessageModel(item, inverted=True)
            tree_view = create_tree_view(self._inverted_messages, (_("Message"),))
            tree_view.set_headers_visible(False)
            frame = Gtk.Frame.new(label=_("Inverted Messages"))
            frame.add(tree_view)
            page.pack_end(frame, True, True, 0)
        else:
            hbox = create_hbox_label(self, page, _("Message sort"))

            sort_data = self.MESSAGE_SORT
            lifeline = None
            cinfo = item.canvas.get_connection(item.tail)
            if cinfo:
                lifeline = cinfo.connected

            # disallow connecting two delete messages to a lifeline
            if (
                lifeline
                and lifeline.is_destroyed
                and subject.messageSort != "deleteMessage"
            ):
                sort_data = list(sort_data)
                assert sort_data[4][1] == "deleteMessage"
                del sort_data[4]

            combo = self.combo = create_uml_combo(
                sort_data, self._on_message_sort_change
            )
            hbox.pack_start(combo, False, True, 0)

            index = combo.get_model().get_index(subject.messageSort)
            combo.set_active(index)

        return page

    @transactional
    def _on_message_sort_change(self, combo):
        """Update message item's message sort information."""

        combo = self.combo
        ms = combo.get_model().get_value(combo.get_active())

        item = self.item
        subject = item.subject
        lifeline = None
        cinfo = item.canvas.get_connection(item.tail)
        if cinfo:
            lifeline = cinfo.connected

        #
        # allow only one delete message to connect to lifeline's lifetime
        # destroyed status can be changed only by delete message itself
        #
        if lifeline:
            if subject.messageSort == "deleteMessage" or not lifeline.is_destroyed:
                is_destroyed = ms == "deleteMessage"
                lifeline.is_destroyed = is_destroyed
                # TODO: is required here?
                lifeline.request_update()

        subject.messageSort = ms
        # TODO: is required here?
        item.request_update()
